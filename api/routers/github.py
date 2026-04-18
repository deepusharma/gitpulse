from fastapi import APIRouter, HTTPException, Depends
import httpx
import logging
import os

from api.dependencies import get_user_repos

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])

@router.get("/validate")
async def validate_github_user(username: str):
    """
    Check if a GitHub user exists and return their profile info.
    """
    logger.info("Validating GitHub user: %s", username)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # Also fetch repos to populate cache and return count
                repos = await get_user_repos(username)
                return {
                    "valid": True, 
                    "username": data["login"], 
                    "avatar_url": data["avatar_url"],
                    "repos": repos
                }
            elif response.status_code == 404:
                return {"valid": False, "error": "User not found"}
            else:
                return {"valid": False, "error": f"GitHub API error: {response.status_code}"}
        except Exception as e:
            logger.error("Error validating user %s: %s", username, e)
            return {"valid": False, "error": str(e)}

@router.get("/repos")
async def get_github_repos(username: str):
    """
    Fetch list of repos for a user (with caching).
    """
    try:
        repos = await get_user_repos(username)
        return {"repos": repos}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error fetching repos for %s: %s", username, e)
        raise HTTPException(status_code=500, detail="Failed to fetch repositories")
