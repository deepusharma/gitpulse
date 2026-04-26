"""FastAPI application for GitPulse."""

import httpx
from collections import Counter
from datetime import datetime, timezone, timedelta
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from api.routers import (
    summarise as summarise_router, 
    history, 
    summary, 
    analytics, 
    github, 
    insights, 
    team, 
    badges, 
    mcp, 
    prompt_templates, 
    deliver,
    health,
    yearly
)
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager

from api.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up GitPulse API v1.4.0")
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

app = FastAPI(title="gitpulse API", version="1.4.0", lifespan=lifespan)

# Register Routers
app.include_router(health.router)
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
app.include_router(yearly.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


