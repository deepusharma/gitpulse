from fastapi import HTTPException, Header
import httpx
from typing import Optional, List
from api.db import get_db_pool
from api.cache import repo_cache
import logging
import os

logger = logging.getLogger(__name__)

def get_db():
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database disabled")
    return pool

async def get_user_repos(username: str) -> List[str]:
    # Check cache first (10 minute expiry)
    repos = repo_cache.get(username)
    if repos:
        logger.info("Using cached repo list for %s", username)
        return repos

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    url = f"https://api.github.com/users/{username}/repos"
    
    async with httpx.AsyncClient() as client:
        params = {"type": "public", "per_page": 100}
        try:
            response = await client.get(url, headers=headers, params=params, timeout=15.0)
            if response.status_code == 401:
                logger.error("GitHub API 401 Unauthorized for %s. Check GITHUB_TOKEN.", username)
                raise HTTPException(status_code=401, detail="GitHub Token is invalid or expired. Please check your .env file.")
            response.raise_for_status()
            data = response.json()
            repos = [repo["name"] for repo in data]
            
            # Update cache
            repo_cache.set(username, repos, ttl=600) # 10 min for repo list
            return repos
        except Exception as e:
            logger.error("Failed to fetch repos for %s: %s", username, e)
            # If fetch fails but we have some cache, return it as fallback (even if expired)
            cached_repos = repo_cache._cache.get(username) # Access internal for fallback
            if cached_repos:
                logger.warning("Returning stale/expired repo list for %s as fallback", username)
                return cached_repos[0]
            raise HTTPException(status_code=500, detail="Failed to fetch user repositories from GitHub")

def get_token_override(x_github_token: Optional[str] = Header(None)) -> Optional[str]:
    return x_github_token
