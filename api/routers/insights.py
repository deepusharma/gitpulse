from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime, timezone, timedelta
import logging
from typing import List, Optional
import os
import asyncio

from api.models import RecommendationsRequest, RecommendationsResponse
from gitpulse.core.repo_reader import get_activity
from gitpulse.core.recommendations import get_recommendations
from api.dependencies import get_user_repos
from api.cache import analytics_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("/metrics")
async def get_insights_metrics(username: str, repos: str, days: int = 30):
    repo_list = [r.strip() for r in repos.split(",") if r.strip()]
    if not repo_list:
        repo_list = await get_user_repos(username)
    if not repo_list: return []
    
    try:
        activity, _ = await get_activity(source="github", username=username, repos=repo_list, days=days)
    except Exception as e:
        logger.error("Failed to fetch activity: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch activity")

    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days - 1)
    
    daily_metrics = {}
    for i in range(days):
        d = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_metrics[d] = {"date": d, "commits": 0, "prs": 0, "issues": 0}
        
    for item in activity.get("commits", []):
        if "date" in item:
            d = item["date"].strftime("%Y-%m-%d")
            if d in daily_metrics: daily_metrics[d]["commits"] += 1
            
    for item in activity.get("prs", []):
        if "merged_at" in item:
            d = item["merged_at"].strftime("%Y-%m-%d")
            if d in daily_metrics: daily_metrics[d]["prs"] += 1
            
    for item in activity.get("issues", []):
        if "closed_at" in item:
            d = item["closed_at"].strftime("%Y-%m-%d")
            if d in daily_metrics: daily_metrics[d]["issues"] += 1
            
    return list(daily_metrics.values())

@router.get("/health")
async def get_insights_health(username: str, repos: str):
    repo_list = [r.strip() for r in repos.split(",") if r.strip()]
    if not repo_list:
        repo_list = await get_user_repos(username)
    if not repo_list: return {"health_score": 0, "repos": []}

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    health_data = []
    total_stars = 0
    total_forks = 0
    total_open_issues = 0

    async with httpx.AsyncClient() as client:
        for repo in repo_list:
            resp = await client.get(f"https://api.github.com/repos/{username}/{repo}", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                stars = data.get("stargazers_count", 0)
                forks = data.get("forks_count", 0)
                open_issues = data.get("open_issues_count", 0)
                
                total_stars += stars
                total_forks += forks
                total_open_issues += open_issues
                
                health_data.append({
                    "repo": repo,
                    "stars": stars,
                    "forks": forks,
                    "open_issues": open_issues
                })
                
    score = 50 + min(total_stars, 30) + min(total_forks * 2, 20) - total_open_issues
    score = max(0, min(100, score))
    
    return {
        "health_score": score,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_open_issues": total_open_issues,
        "repos": health_data
    }

@router.post("/recommendations", response_model=RecommendationsResponse)
async def insights_recommendations(req: RecommendationsRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")

    cache_key = f"recommendations:{req.username}:{req.days}"
    cached = analytics_cache.get(cache_key)
    if cached:
        logger.info("Using cached recommendations for %s", req.username)
        return RecommendationsResponse(**cached)

    db_commits = 0
    db_prs = 0
    db_issues = 0
    stale_prs = 0
    avg_cycle_time_hrs = 0.0
    prev_commits = 0
    streak = 0

    try:
        repos = await get_user_repos(req.username)
        if repos:
            activity, _ = await get_activity(
                source="github", username=req.username, repos=repos, days=req.days
            )
            db_commits = len(activity.get("commits", []))
            db_prs = len(activity.get("prs", []))
            db_issues = len(activity.get("issues", []))

            now = datetime.now(timezone.utc)
            prs = activity.get("prs", [])
            stale_prs = sum(
                1 for p in prs
                if (now - p["merged_at"]).total_seconds() / 3600 > 7 * 24
            )

            commit_dates = sorted(
                {c["date"].date() for c in activity.get("commits", [])},
                reverse=True,
            )
            if commit_dates:
                check = commit_dates[0]
                for d in commit_dates:
                    if d == check:
                        streak += 1
                        check = check - timedelta(days=1)
                    else:
                        break

            full_activity, _ = await get_activity(
                source="github", username=req.username, repos=repos, days=req.days * 2
            )
            split_date = now - timedelta(days=req.days)
            prev_commits = sum(
                1 for c in full_activity.get("commits", [])
                if c["date"] < split_date
            )
    except Exception as exc:
        logger.error("Failed to gather metrics for recommendations: %s", exc, exc_info=True)

    metrics = {
        "commits": db_commits,
        "prs": db_prs,
        "issues": db_issues,
        "avg_cycle_time_hrs": avg_cycle_time_hrs,
        "stale_prs": stale_prs,
        "commit_streak_days": streak,
        "prev_commits": prev_commits,
    }

    try:
        nudges = await get_recommendations(metrics)
    except Exception as exc:
        logger.error("get_recommendations failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"recommendations": nudges, "generated_at": generated_at}
    analytics_cache.set(cache_key, result, ttl=600)

    return RecommendationsResponse(**result)
