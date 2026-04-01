"""FastAPI application for GitPulse."""

import httpx
from collections import Counter
from datetime import datetime, timezone, timedelta
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.repo_reader import get_commits
from core.summarise import format_commits, to_prompt_str, to_display_str, build_prompt, summarise

from contextlib import asynccontextmanager
import os

from api.db import init_db, close_db, get_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(title="gitpulse API", version="0.5.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SummariseRequest(BaseModel):
    username: str
    repos: List[str]
    days: int = 7

class SummariseResponse(BaseModel):
    display: str
    summary: str
    repos: List[str]
    days: int
    generated_at: str

# Routes
@app.get("/health")
async def health():
    """
    Health check endpoint.
    
    Returns:
        dict: Status and version of the API.
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok", "version": "0.5.0"}

@app.post("/summarise", response_model=SummariseResponse)
async def create_summary(request: SummariseRequest):
    """
    Generate a summary of commits for a given user and repositories.
    
    Args:
        request (SummariseRequest): The request payload containing username, repos, and days.
        
    Returns:
        SummariseResponse: The generated summary and associated metadata.
        
    Raises:
        HTTPException: If validation fails or downstream errors occur.
    """
    logger.info("Received summarise request for username: %s, repos: %s", request.username, request.repos)

    if not request.username:
        logger.warning("Summarise request failed validation: missing username")
        raise HTTPException(status_code=422, detail="Username cannot be empty")
    if not request.repos:
        logger.warning("Summarise request failed validation: missing repos")
        raise HTTPException(status_code=422, detail="Repos list cannot be empty")

    try:
        # Calls the GitHub API adapter
        commits = get_commits(
            source="github",
            username=request.username,
            repos=request.repos,
            days=request.days
        )
        
        formatted = format_commits(commits)
        prompt_str = to_prompt_str(formatted)
        display_str = to_display_str(formatted)
        
        prompt = build_prompt(prompt_str)
        summary = summarise(prompt)
        
        generated_at = datetime.now(timezone.utc)
        
        logger.info("Successfully generated summary for username: %s", request.username)
        
        # Save to DB if pool is available
        pool = get_db_pool()
        if pool:
            try:
                async with pool.acquire() as connection:
                    await connection.execute(
                        '''
                        INSERT INTO summaries (username, repos, days, display, summary, generated_at)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ''',
                        request.username, request.repos, request.days, display_str, summary, generated_at
                    )
                logger.info("Saved summary to database for username: %s", request.username)
            except Exception as db_e:
                logger.error("Failed to save summary to database: %s", db_e, exc_info=True)

        return SummariseResponse(
            display=display_str,
            summary=summary,
            repos=request.repos,
            days=request.days,
            generated_at=generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    except ValueError as e:
        logger.error("msg: %s", e, exc_info=True)
        msg = str(e)
        if "not found or is private" in msg:
            raise HTTPException(status_code=404, detail={"error": msg, "code": 404})
        elif "rate limit" in msg:
            raise HTTPException(status_code=429, detail={"error": "GitHub API rate limit exceeded. Try again in 60 minutes.", "code": 429})
        elif "unauthorised" in msg:
            raise HTTPException(status_code=401, detail={"error": "GitHub API unauthorised \u2014 check GITHUB_TOKEN", "code": 401})
        else:
            raise HTTPException(status_code=500, detail={"error": "Failed to generate summary. Please try again.", "code": 500})
    except Exception as e:
        logger.error("msg: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail={"error": "Failed to generate summary. Please try again.", "code": 500})

@app.get("/history")
async def get_history(username: str, limit: int = 10):
    """
    Fetch historical summaries for a given username.
    """
    logger.info("Fetching history for username: %s (limit: %d)", username, limit)
    pool = get_db_pool()
    if not pool:
        logger.warning("DB pool not initialized. Cannot fetch history.")
        return {"summaries": [], "total": 0}

    try:
        async with pool.acquire() as connection:
            records = await connection.fetch(
                '''
                SELECT id, username, repos, days, summary, generated_at
                FROM summaries
                WHERE username = $1
                ORDER BY generated_at DESC
                LIMIT $2
                ''',
                username, limit
            )
            
            # Count total
            total_count = await connection.fetchval(
                'SELECT COUNT(*) FROM summaries WHERE username = $1',
                username
            )
            
            return {
                "summaries": [
                    {
                        "id": str(r["id"]),
                        "username": r["username"],
                        "repos": r["repos"],
                        "days": r["days"],
                        "summary": r["summary"],
                        "generated_at": r["generated_at"].strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    for r in records
                ],
                "total": total_count or 0
            }
    except Exception as e:
        logger.error("msg: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail={"error": "Failed to fetch history.", "code": 500})

def _get_user_repos(username: str) -> list[str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    url = f"https://api.github.com/users/{username}/repos"
    repos = []
    
    with httpx.Client() as client:
        params = {"type": "public", "per_page": 100}
        try:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            repos = [repo["name"] for repo in data]
        except Exception as e:
            logger.error("Failed to fetch repos for %s: %s", username, e)
            raise HTTPException(status_code=500, detail="Failed to fetch user repositories from GitHub")
    return repos

@app.get("/analytics/commits-per-day")
async def get_commits_per_day(username: str, days: int = 30):
    repos = _get_user_repos(username)
    if not repos:
        return []
    
    try:
        commits = get_commits(source="github", username=username, repos=repos, days=days)
    except Exception as e:
        logger.error("Failed to fetch commits: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch commits")
        
    counts = Counter()
    for commit in commits:
        date_str = commit["date"].strftime("%Y-%m-%d")
        counts[date_str] += 1
        
    result = [{"date": k, "count": v} for k, v in sorted(counts.items())]
    return result

@app.get("/analytics/repos-breakdown")
async def get_repos_breakdown(username: str, days: int = 30):
    repos = _get_user_repos(username)
    if not repos:
        return []
        
    try:
        commits = get_commits(source="github", username=username, repos=repos, days=days)
    except Exception as e:
        logger.error("Failed to fetch commits: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch commits")
        
    counts = Counter()
    for commit in commits:
        counts[commit["repo"]] += 1
        
    total_commits = sum(counts.values())
    
    result = []
    if total_commits > 0:
        for repo, count in counts.items():
            result.append({
                "repo": repo,
                "count": count,
                "percentage": round((count / total_commits) * 100, 1)
            })
    return sorted(result, key=lambda x: x["count"], reverse=True)

@app.get("/analytics/insights")
async def get_insights(username: str, days: int = 30):
    # Get total summaries from DB
    pool = get_db_pool()
    total_summaries = 0
    if pool:
        try:
            async with pool.acquire() as conn:
                count = await conn.fetchval('SELECT COUNT(*) FROM summaries WHERE username = $1', username)
                total_summaries = count or 0
        except Exception as e:
            logger.error("DB error figuring out summaries count: %s", e)
            
    repos = _get_user_repos(username)
    if not repos:
        return {"most_active_day": "N/A", "streak": 0, "top_repo": "N/A", "total_summaries": total_summaries, "average_commits_per_day": 0}
        
    try:
        commits = get_commits(source="github", username=username, repos=repos, days=days)
    except Exception as e:
        logger.error("Failed to fetch commits: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch commits")
    
    if not commits:
        return {"most_active_day": "N/A", "streak": 0, "top_repo": "N/A", "total_summaries": total_summaries, "average_commits_per_day": 0}

    day_counts = Counter()
    repo_counts = Counter()
    date_set = set()
    
    for c in commits:
        day_str = c["date"].strftime("%A")
        day_counts[day_str] += 1
        repo_counts[c["repo"]] += 1
        date_set.add(c["date"].date())
        
    most_active_day = day_counts.most_common(1)[0][0] if day_counts else "N/A"
    top_repo = repo_counts.most_common(1)[0][0] if repo_counts else "N/A"
    
    streak = 0
    if date_set:
        sorted_dates = sorted(list(date_set), reverse=True)
        current_date_val = datetime.now(timezone.utc).date()
        
        if sorted_dates[0] < current_date_val - timedelta(days=1):
            streak = 0
        else:
            check_date = sorted_dates[0]
            for d in sorted_dates:
                if d == check_date:
                    streak += 1
                    check_date = check_date - timedelta(days=1)
                else:
                    break
    
    average_commits = round(len(commits) / days, 1)
    
    return {
        "most_active_day": most_active_day,
        "streak": streak,
        "top_repo": top_repo,
        "total_summaries": total_summaries,
        "average_commits_per_day": average_commits
    }
