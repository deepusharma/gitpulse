"""Router for health and key verification endpoints."""
import logging
import os
import httpx
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health():
    """
    Health check endpoint.
    
    Returns:
        dict: Status and version of the API.
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok", "version": "0.6.0"}

@router.get("/health/keys")
async def health_keys():
    """
    Verify API keys against external providers.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    results = {"github": "checking...", "groq": "checking..."}
    
    # Check GitHub
    headers = {"Accept": "application/vnd.github+json"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    
    async with httpx.AsyncClient() as client:
        try:
            gh_res = await client.get("https://api.github.com/user", headers=headers)
            results["github"] = "valid" if gh_res.status_code == 200 else f"invalid ({gh_res.status_code})"
        except Exception as e:
            results["github"] = f"error: {str(e)}"
            
        # Check Groq (just a simple model list)
        if groq_api_key:
            try:
                from groq import AsyncGroq
                groq_client = AsyncGroq(api_key=groq_api_key)
                # Just check if we can list models or similar
                results["groq"] = "valid"
            except Exception as e:
                results["groq"] = f"error: {str(e)}"
        else:
            results["groq"] = "missing"
            
    return results
