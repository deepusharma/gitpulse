"""FastAPI application for GitPulse."""

import httpx
from collections import Counter
from datetime import datetime, timezone, timedelta
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from api.routers import summarise as summarise_router, history, summary, analytics, github, insights, team, badges, mcp, prompt_templates, deliver
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from gitpulse.core.repo_reader import get_activity
from gitpulse.core.summarise import format_activity, to_prompt_str, to_display_str, build_prompt, summarise
from gitpulse.core.recommendations import get_recommendations

from contextlib import asynccontextmanager
import os

from api.db import init_db, close_db, get_db_pool

from api.cache import InMemoryCache, repo_cache, commit_cache, analytics_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up GitPulse API v0.7.0")
    if not os.getenv("GROQ_API_KEY"):
        logger.error("CRITICAL: GROQ_API_KEY is not set. Summary generation will fail.")
    try:
        await init_db()
    except Exception as e:
        logger.error("CRITICAL: DB initialization failed. Running in DEGRADED MODE (no history). Error: %s", e)
    yield
    # Shutdown
    try:
        await close_db()
    except Exception: pass

app = FastAPI(title="gitpulse API", version="0.6.0", lifespan=lifespan)
app.include_router(summarise_router.router)
app.include_router(history.router)
app.include_router(summary.router)
app.include_router(analytics.router)
app.include_router(github.router)
app.include_router(insights.router)
app.include_router(team.router)
app.include_router(badges.router)
app.include_router(mcp.router)
app.include_router(prompt_templates.router)
app.include_router(deliver.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.models import *

# Routes
@app.get("/health")
async def health():
    """
    Health check endpoint.
    
    Returns:
        dict: Status and version of the API.
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok", "version": "0.6.0"}

@app.get("/health/keys")
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
                # Simple ping:
                results["groq"] = "valid"
            except Exception as e:
                results["groq"] = f"error: {str(e)}"
        else:
            results["groq"] = "missing"
            
    return results


