"""FastAPI application for GitPulse."""

from datetime import datetime, timezone
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

logger = logging.getLogger(__name__)

from core.repo_reader import get_commits
from core.summarise import format_commits, to_prompt_str, to_display_str, build_prompt, summarise

app = FastAPI(title="gitpulse API", version="0.2.0")

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
    return {"status": "ok", "version": "0.2.0"}

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
        
        logger.info("Successfully generated summary for username: %s", request.username)
        return SummariseResponse(
            display=display_str,
            summary=summary,
            repos=request.repos,
            days=request.days,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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
