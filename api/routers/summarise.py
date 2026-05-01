from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime, timezone
import logging
import os

from api.models import SummariseRequest, SummariseResponse
from api.dependencies import get_token_override, get_db
from api.cache import commit_cache
from gitpulse.core.repo_reader import get_activity
from gitpulse.core.summarise import format_activity, to_prompt_str, to_display_str, build_prompt, summarise

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/summarise", response_model=SummariseResponse)
async def create_summary(
    request: SummariseRequest, 
    refresh: bool = False,
    x_github_token: Optional[str] = Depends(get_token_override)
):
    """
    Generate a summary of commits for a given user and repositories.
    """
    logger.info("Received summarise request for username: %s, repos: %s", request.username, request.repos)
    
    # 1. Check cache first
    cache_key = f"summary:{request.username}:{','.join(sorted(request.repos))}:{request.days}:{request.tone}:{request.language}"
    if not refresh:
        cached_result = commit_cache.get(cache_key)
        if cached_result:
            logger.info("Using cached summary for %s", request.username)
            return SummariseResponse(**cached_result)

    if not request.username:
        logger.warning("Summarise request failed validation: missing username")
        raise HTTPException(status_code=422, detail="Username cannot be empty")
    if not request.repos:
        logger.warning("Summarise request failed validation: missing repos")
        raise HTTPException(status_code=422, detail="Repos list cannot be empty")

    try:
        # Calls the GitHub API adapter
        activity, errors = await get_activity(
            source="github",
            username=request.username,
            repos=request.repos,
            days=request.days,
            token=x_github_token
        )
        commits = activity.get("commits", [])
        
        if not commits and errors:
            error_msg = errors[0]
            if "not found or is private" in error_msg.lower() or "not found" in error_msg.lower():
                logger.error("Repo error: %s", error_msg)
                raise HTTPException(status_code=404, detail={"error": error_msg, "code": 404})
            elif "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail={"error": error_msg, "code": 429})
            else:
                raise Exception(error_msg)

        generated_at = datetime.now(timezone.utc)
        
        if len(commits) == 0 and len(activity.get("prs", [])) == 0 and len(activity.get("issues", [])) == 0:
            logger.info("No activity found for %s over the last %s days", request.username, request.days)
            res = {
                "id": "none",
                "display": "No activity found.",
                "summary": "No activity found.",
                "repos": request.repos,
                "username": request.username,
                "days": request.days,
                "generated_at": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "is_public": False
            }
            return res
            
        formatted = format_activity(activity)
        prompt_str = to_prompt_str(formatted)
        display_str = to_display_str(formatted)
        
        prompt = build_prompt(prompt_str, tone=request.tone, language=request.language)
        summary = await summarise(prompt)
        
        logger.info("Successfully generated summary for username: %s", request.username)
        
        summary_id = "none"
        # Save to DB if pool is available
        from api.db import get_db_pool
        pool = get_db_pool()
        if pool:
            try:
                async with pool.acquire() as connection:
                    row = await connection.fetchrow(
                        '''
                        INSERT INTO summaries (username, repos, days, display, summary, generated_at)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING id
                        ''',
                        request.username, request.repos, request.days, display_str, summary, generated_at
                    )
                    summary_id = str(row['id'])
                logger.info("Saved summary to database with id: %s", summary_id)
            except Exception as db_e:
                logger.error("Failed to save summary to database: %s", db_e, exc_info=True)

        result = {
            "id": summary_id,
            "display": display_str,
            "summary": summary,
            "repos": request.repos,
            "username": request.username,
            "days": request.days,
            "generated_at": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "is_public": False
        }
        
        # Update cache
        commit_cache.set(cache_key, result, ttl=300)
        
        return SummariseResponse(**result)
    except Exception as e:
        logger.error("Error during summary generation: %s", e, exc_info=True)
        msg = str(e)
        if "not found or is private" in msg:
            raise HTTPException(status_code=404, detail={"error": "Repository not found or private.", "code": 404})
        elif "rate limit" in msg.lower() or "RateLimitError" in msg:
            raise HTTPException(status_code=429, detail={"error": "API rate limit exceeded. Please try again later.", "code": 429})
        elif "authentication" in msg.lower() or "AuthenticationError" in msg:
            raise HTTPException(status_code=401, detail={"error": "API Authentication failed. Check your API keys.", "code": 401})
        else:
            import traceback
            tb = traceback.format_exc()
            logger.error("Internal Error Traceback: %s", tb)
            raise HTTPException(status_code=500, detail={
                "error": "Failed to generate summary. Internal server error.",
                "traceback": tb if os.getenv("DEBUG", "false").lower() == "true" else None,
                "code": 500
            })
