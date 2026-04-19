from fastapi import APIRouter, HTTPException
import logging
from typing import List
import os
import asyncio
from datetime import datetime, timezone

from api.models import RosterRequest, RosterResponse, TeamSummariseRequest, TeamSummariseResponse
from api.db import get_db_pool
from gitpulse.core.repo_reader import get_activity
from gitpulse.core.summarise import format_activity, to_prompt_str, to_display_str, build_prompt, summarise

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/team", tags=["team"])

@router.post("/roster", response_model=RosterResponse)
async def create_or_update_roster(req: RosterRequest):
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database disabled")
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow('''
                INSERT INTO rosters (name, usernames)
                VALUES ($1, $2)
                RETURNING id, name, usernames, created_at
            ''', req.name, req.usernames)
            return RosterResponse(
                id=str(row['id']),
                name=row['name'],
                usernames=row['usernames'],
                created_at=row['created_at'].isoformat()
            )
    except Exception as e:
        logger.error("Failed to save roster: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save roster")

@router.get("/rosters", response_model=List[RosterResponse])
async def list_rosters():
    pool = get_db_pool()
    if not pool: return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, name, usernames, created_at FROM rosters
                ORDER BY created_at DESC
            ''')
            return [RosterResponse(
                id=str(r['id']),
                name=r['name'],
                usernames=r['usernames'],
                created_at=r['created_at'].isoformat()
            ) for r in rows]
    except Exception as e:
        logger.error("Failed to list rosters: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list rosters")

@router.get("/roster/{roster_id}", response_model=RosterResponse)
async def get_roster(roster_id: str):
    pool = get_db_pool()
    if not pool: raise HTTPException(status_code=503, detail="Database disabled")
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT id, name, usernames, created_at FROM rosters WHERE id::text = $1
            ''', roster_id)
            if not row:
                raise HTTPException(status_code=404, detail="Roster not found")
            return RosterResponse(
                id=str(row['id']),
                name=row['name'],
                usernames=row['usernames'],
                created_at=row['created_at'].isoformat()
            )
    except HTTPException: raise
    except Exception as e:
        logger.error("Failed to get roster: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get roster")

@router.delete("/roster/{roster_id}")
async def delete_roster(roster_id: str):
    pool = get_db_pool()
    if not pool: raise HTTPException(status_code=503, detail="Database disabled")
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM rosters WHERE id::text = $1", roster_id)
            return {"status": "deleted", "id": roster_id}
    except Exception as e:
        logger.error("Failed to delete roster: %s", e)
        raise HTTPException(status_code=500, detail="Failed to delete roster")

@router.post("/summarise", response_model=TeamSummariseResponse)
async def team_summarise(req: TeamSummariseRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="LLM not configured (missing Groq API key).")
    
    unique_repos = list(set([r.strip() for r in req.repos if r.strip()]))
    unique_users = list(set([u.strip() for u in req.usernames if u.strip()]))
    if not unique_repos:
        raise HTTPException(status_code=422, detail="No valid repositories provided.")
    if not unique_users:
        raise HTTPException(status_code=422, detail="No valid usernames provided.")
        
    async def fetch_user_activity(user: str):
        try:
            return await get_activity(source="github", username=user, repos=unique_repos, days=req.days)
        except Exception as e:
            logger.error("Failed user %s: %s", user, e)
            return ({"commits": [], "prs": [], "issues": []}, [])

    results = await asyncio.gather(*[fetch_user_activity(u) for u in unique_users])
    
    combined_activity = {"commits": [], "prs": [], "issues": []}
    for activity, _ in results:
        combined_activity["commits"].extend(activity.get("commits", []))
        combined_activity["prs"].extend(activity.get("prs", []))
        combined_activity["issues"].extend(activity.get("issues", []))
        
    if not any(combined_activity.values()):
        display = "### No activity found\nNo recent activity across the team in the specified repositories."
        summary = "# WHAT WE DID\n* No tracked activity over the specified period."
        return TeamSummariseResponse(
            display=display, summary=summary, repos=unique_repos,
            days=req.days, contributors=unique_users,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
        
    formatted = format_activity(combined_activity)
    display_str = to_display_str(formatted)
    prompt_str = to_prompt_str(formatted)
    prompt = build_prompt(prompt_str)
    
    try:
        summary_md = await summarise(prompt)
    except Exception as e:
        logger.error("Groq generation failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate AI summary.")
        
    return TeamSummariseResponse(
        display=display_str, summary=summary_md, repos=unique_repos,
        days=req.days, contributors=unique_users,
        generated_at=datetime.now(timezone.utc).isoformat()
    )
