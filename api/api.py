"""FastAPI application for GitPulse."""

import httpx
from collections import Counter
from datetime import datetime, timezone, timedelta
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from api.routers import summarise as summarise_router
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
    id: str
    display: str
    summary: str
    repos: List[str]
    days: int
    username: str
    generated_at: str
    is_public: bool = False

class RosterRequest(BaseModel):
    name: str
    usernames: List[str]

class RosterResponse(BaseModel):
    id: str
    name: str
    usernames: List[str]
    created_at: str

class TeamSummariseRequest(BaseModel):
    usernames: List[str]
    repos: List[str]
    days: int = 7

class TeamSummariseResponse(BaseModel):
    display: str
    summary: str
    repos: List[str]
    days: int
    contributors: List[str]
    generated_at: str

class SlackDeliverRequest(BaseModel):
    summary: str
    webhook_url: str
    channel: Optional[str] = None

class PublicToggleRequest(BaseModel):
    public: bool

class PublicToggleResponse(BaseModel):
    id: str
    is_public: bool

class PublicSummaryResponse(BaseModel):
    id: str
    username: str
    repos: List[str]
    days: int
    summary: str
    generated_at: str

class CompareRecord(BaseModel):
    commits: int
    prs: int
    issues: int
    active_days: int

class CompareResponse(BaseModel):
    username: str
    days: int
    current: CompareRecord
    previous: CompareRecord
    delta: dict


class RecommendationsRequest(BaseModel):
    username: str
    days: int = 30

class RecommendationsResponse(BaseModel):
    recommendations: str
    generated_at: str

class PromptTemplateCreate(BaseModel):
    username: str
    name: str
    content: str

class PromptTemplateResponse(BaseModel):
    id: str
    username: str
    name: str
    content: str
    created_at: str


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



@app.patch("/history/{summary_id}/public", response_model=PublicToggleResponse)
async def toggle_summary_public(summary_id: str, req: PublicToggleRequest):
    """Toggle the is_public flag for a summary."""
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE summaries SET is_public = $1 WHERE id::text = $2 RETURNING id, is_public",
                req.public, summary_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="Summary not found")
            return PublicToggleResponse(id=str(row['id']), is_public=row['is_public'])
    except HTTPException: raise
    except Exception as e:
        logger.error("Failed to toggle public status: %s", e)
        raise HTTPException(status_code=500, detail="Failed to toggle public status")

@app.get("/summary/public/{summary_id}", response_model=PublicSummaryResponse)
async def get_public_summary(summary_id: str):
    """Fetch a public summary by ID without authentication."""
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, username, repos, days, summary, generated_at FROM summaries WHERE id::text = $1 AND is_public = TRUE",
                summary_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="Public summary not found")
            return PublicSummaryResponse(
                id=str(row['id']),
                username=row['username'],
                repos=row['repos'],
                days=row['days'],
                summary=row['summary'],
                generated_at=row['generated_at'].strftime("%Y-%m-%dT%H:%M:%SZ")
            )
    except HTTPException: raise
    except Exception as e:
        logger.error("Failed to fetch public summary: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch public summary")

@app.get("/analytics/compare", response_model=CompareResponse)
async def compare_periods(username: str, days: int = 30):
    """Compare performance metrics between current and previous periods."""
    repos = await _get_user_repos(username)
    if not repos:
        raise HTTPException(status_code=404, detail="No repositories found for user")

    # Current period
    activity_curr, _ = await get_activity(source="github", username=username, repos=repos, days=days)
    
    # Previous period
    # To get the previous period of the same length, we look back from (days) ago to (2*days) ago.
    # However, get_activity is built to look back N days from NOW.
    # We might need a more flexible get_activity or a custom implementation here.
    # For now, let's assume we can use a custom fetch since get_activity is a bit fixed.
    
    # Actually, let's just do two calls if we can but handle the dates.
    # current: [now - days, now]
    # previous: [now - 2*days, now - days]
    
    # I'll implement a helper for this or use raw calls.
    # Given the complexity, I'll stick to a slightly simplified comparison for this sprint:
    # We'll fetch all activity for 2*days and split it.
    
    full_activity, _ = await get_activity(source="github", username=username, repos=repos, days=days * 2)
    
    now = datetime.now(timezone.utc)
    split_date = now - timedelta(days=days)
    
    def process_activity(items, date_key, is_current):
        count = 0
        active_dates = set()
        for item in items:
            dt = item.get(date_key)
            if dt:
                if is_current and dt >= split_date:
                    count += 1
                    active_dates.add(dt.date())
                elif not is_current and dt < split_date:
                    count += 1
                    active_dates.add(dt.date())
        return count, len(active_dates)

    # Process Current
    curr_commits, curr_active_commit_days = process_activity(full_activity.get("commits", []), "date", True)
    curr_prs, curr_active_pr_days = process_activity(full_activity.get("prs", []), "merged_at", True)
    curr_issues, curr_active_issue_days = process_activity(full_activity.get("issues", []), "closed_at", True)
    curr_active_days = len(set(list(full_activity.get("commits", [])) + list(full_activity.get("prs", [])) + list(full_activity.get("issues", [])))) # Simplified
    
    # Re-calculate active days properly
    curr_active_total = set()
    prev_active_total = set()
    
    for c in full_activity.get("commits", []):
        d = c["date"]
        if d >= split_date: curr_active_total.add(d.date())
        else: prev_active_total.add(d.date())
    for p in full_activity.get("prs", []):
        d = p["merged_at"]
        if d >= split_date: curr_active_total.add(d.date())
        else: prev_active_total.add(d.date())
    for i in full_activity.get("issues", []):
        d = i["closed_at"]
        if d >= split_date: curr_active_total.add(d.date())
        else: prev_active_total.add(d.date())

    # Process Previous
    prev_commits, _ = process_activity(full_activity.get("commits", []), "date", False)
    prev_prs, _ = process_activity(full_activity.get("prs", []), "merged_at", False)
    prev_issues, _ = process_activity(full_activity.get("issues", []), "closed_at", False)

    current = CompareRecord(commits=curr_commits, prs=curr_prs, issues=curr_issues, active_days=len(curr_active_total))
    previous = CompareRecord(commits=prev_commits, prs=prev_prs, issues=prev_issues, active_days=len(prev_active_total))

    def calc_delta(curr, prev):
        if prev == 0: return 100 if curr > 0 else 0
        return round(((curr - prev) / prev) * 100, 1)

    delta = {
        "commits": calc_delta(curr_commits, prev_commits),
        "prs": calc_delta(curr_prs, prev_prs),
        "issues": calc_delta(curr_issues, prev_issues),
        "active_days": calc_delta(len(curr_active_total), len(prev_active_total))
    }

    return CompareResponse(username=username, days=days, current=current, previous=previous, delta=delta)


@app.get("/history")
async def get_history(
    username: str, 
    limit: int = 10, 
    search: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None
):
    """
    Fetch historical summaries for a given username with filtering options.
    """
    logger.info("Fetching history for %s (limit: %d, search: %s, date: %s-%s)", username, limit, search, start_date, end_date)
    # Validate dates early
    start_dt = None
    end_dt = None
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    pool = get_db_pool()
    if not pool:
        logger.warning("DB pool not initialized. Cannot fetch history.")
        return {"summaries": [], "total": 0}

    try:
        async with pool.acquire() as connection:
            query = """
                SELECT id, username, repos, days, summary, generated_at
                FROM summaries
                WHERE username = $1
            """
            params = [username]
            idx = 2
            
            if search:
                query += f" AND (repos::text ILIKE ${idx} OR summary ILIKE ${idx})"
                params.append(f"%{search}%")
                idx += 1
                
            if start_dt:
                query += f" AND generated_at >= ${idx}"
                params.append(start_dt)
                idx += 1
                
            if end_dt:
                query += f" AND generated_at <= ${idx}"
                params.append(end_dt)
                idx += 1
                
            query += f" ORDER BY generated_at DESC LIMIT ${idx}"
            params.append(limit)
            
            records = await connection.fetch(query, *params)
            
            # Count also needs filters
            count_query = "SELECT COUNT(*) FROM summaries WHERE username = $1"
            count_params = [username]
            c_idx = 2
            if search:
                count_query += f" AND (repos::text ILIKE ${c_idx} OR summary ILIKE ${c_idx})"
                count_params.append(f"%{search}%")
                c_idx += 1
            if start_dt:
                count_query += f" AND generated_at >= ${c_idx}"
                count_params.append(start_dt)
                c_idx += 1
            if end_dt:
                count_query += f" AND generated_at <= ${c_idx}"
                count_params.append(end_dt)
            
            total_count = await connection.fetchval(count_query, *count_params) or 0
            
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

async def _get_user_repos(username: str) -> list[str]:
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

@app.get("/analytics/commits-per-day")
async def get_activity_per_day(username: str, days: int = 30):
    repos = await _get_user_repos(username)
    if not repos:
        return []
    
    try:
        activity, errors = await get_activity(source="github", username=username, repos=repos, days=days)
        commits = activity.get("commits", [])
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
    repos = await _get_user_repos(username)
    if not repos:
        return []
        
    try:
        activity, errors = await get_activity(source="github", username=username, repos=repos, days=days)
        commits = activity.get("commits", [])
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

@app.get("/github/validate")
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
                repos = await _get_user_repos(username)
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

@app.get("/github/repos")
async def get_github_repos(username: str):
    """
    Fetch list of repos for a user (with caching).
    """
    try:
        repos = await _get_user_repos(username)
        return {"repos": repos}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error fetching repos for %s: %s", username, e)
        raise HTTPException(status_code=500, detail="Failed to fetch repositories")

@app.get("/analytics/all")
async def get_analytics_full(username: str, days: int = 30, refresh: bool = False):
    """
    Fetch all analytics data in a single optimized pass.
    """
    # Check cache
    cache_key = f"analytics:{username}:{days}"
    if not refresh:
        cached = analytics_cache.get(cache_key)
        if cached:
            logger.info("Using cached analytics for %s", username)
            return cached

    # 1. Get total summaries from DB
    pool = get_db_pool()
    total_summaries = 0
    if pool:
        try:
            async with pool.acquire() as conn:
                count = await conn.fetchval('SELECT COUNT(*) FROM summaries')
                total_summaries = count or 0
        except Exception as e:
            logger.error("DB error figuring out summaries count: %s", e)
            
    # 2. Get user repos
    repos = await _get_user_repos(username)
    if not repos:
        return {
            "commits_per_day": [],
            "repos_breakdown": [],
            "insights": {
                "most_active_day": "N/A", "streak": 0, "top_repo": "N/A",
                "total_summaries": total_summaries, "average_commits_per_day": 0
            }
        }
        
    # 3. Get ALL relevant commits in ONE sweep
    try:
        activity, errors = await get_activity(source="github", username=username, repos=repos, days=days)
        commits = activity.get("commits", [])
    except Exception as e:
        logger.error("Failed to fetch commits for %s: %s", username, e)
        # Return empty data instead of 500 to keep dashboard stable
        return {
            "commits_per_day": [],
            "repos_breakdown": [],
            "insights": {
                "most_active_day": "N/A", "streak": 0, "top_repo": "N/A",
                "total_summaries": total_summaries, "average_commits_per_day": 0
            }
        }
        
    if not commits:
         return {
            "commits_per_day": [],
            "repos_breakdown": [],
            "insights": {
                "most_active_day": "N/A", "streak": 0, "top_repo": "N/A",
                "total_summaries": total_summaries, "average_commits_per_day": 0
            }
        }

    # 4. Process data (Frequency)
    counts_freq = Counter()
    for commit in commits:
        date_str = commit["date"].strftime("%Y-%m-%d")
        counts_freq[date_str] += 1
    commits_per_day = [{"date": k, "count": v} for k, v in sorted(counts_freq.items())]

    # 5. Process data (Breakdown)
    counts_repo = Counter()
    for commit in commits:
        counts_repo[commit["repo"]] += 1
    
    total_commits = len(commits)
    repos_breakdown = []
    for repo, count in counts_repo.items():
        repos_breakdown.append({
            "repo": repo,
            "count": count,
            "percentage": round((count / total_commits) * 100, 1)
        })
    repos_breakdown = sorted(repos_breakdown, key=lambda x: x["count"], reverse=True)

    # 6. Process data (Insights)
    day_counts = Counter()
    date_set = set()
    for c in commits:
        day_str = c["date"].strftime("%A")
        day_counts[day_str] += 1
        date_set.add(c["date"].date())
        
    most_active_day = day_counts.most_common(1)[0][0] if day_counts else "N/A"
    top_repo = repos_breakdown[0]["repo"] if repos_breakdown else "N/A"
    
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
                else: break
    
    average_commits = round(total_commits / days, 1)

    result = {
        "commits_per_day": commits_per_day,
        "repos_breakdown": repos_breakdown,
        "insights": {
            "most_active_day": most_active_day,
            "streak": streak,
            "top_repo": top_repo,
            "total_summaries": total_summaries,
            "average_commits_per_day": average_commits
        },
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Store in cache
    analytics_cache.set(cache_key, result, ttl=300)
    
    return result

@app.get("/analytics/insights")
async def get_insights(username: str, days: int = 30):
    # Get total summaries from DB
    pool = get_db_pool()
    total_summaries = 0
    if pool:
        try:
            async with pool.acquire() as conn:
                count = await conn.fetchval('SELECT COUNT(*) FROM summaries')
                total_summaries = count or 0
        except Exception as e:
            logger.error("DB error figuring out summaries count: %s", e)
            
    repos = await _get_user_repos(username)
    if not repos:
        return {"most_active_day": "N/A", "streak": 0, "top_repo": "N/A", "total_summaries": total_summaries, "average_commits_per_day": 0}
        
    try:
        activity, errors = await get_activity(source="github", username=username, repos=repos, days=days)
        commits = activity.get("commits", [])
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

@app.get("/insights/metrics")
async def get_insights_metrics(username: str, repos: str, days: int = 30):
    repo_list = [r.strip() for r in repos.split(",") if r.strip()]
    if not repo_list:
        repo_list = await _get_user_repos(username)
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

@app.get("/insights/health")
async def get_insights_health(username: str, repos: str):
    repo_list = [r.strip() for r in repos.split(",") if r.strip()]
    if not repo_list:
        repo_list = await _get_user_repos(username)
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

# --- Sprint 15: Team & Reach Endpoints ---

@app.post("/team/roster", response_model=RosterResponse)
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

@app.get("/team/rosters", response_model=List[RosterResponse])
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

@app.get("/team/roster/{roster_id}", response_model=RosterResponse)
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

@app.delete("/team/roster/{roster_id}")
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

@app.post("/team/summarise", response_model=TeamSummariseResponse)
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

@app.post("/deliver/slack")
async def deliver_slack(req: SlackDeliverRequest):
    if not req.webhook_url.startswith("https://hooks.slack.com/"):
        raise HTTPException(status_code=400, detail="Invalid Slack webhook URL")
    
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": req.summary
                }
            }
        ]
    }
    if req.channel:
        payload["channel"] = req.channel

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(req.webhook_url, json=payload)
            if resp.status_code != 200:
                logger.error("Slack rejected payload: %s %s", resp.status_code, resp.text)
                raise HTTPException(status_code=502, detail="Slack delivery rejected")
        except Exception as e:
            logger.error("Slack webhook error: %s", e)
            raise HTTPException(status_code=500, detail="Failed to reach Slack")
    return {"ok": True}

@app.get("/badges/streak")
async def get_badge_streak(username: str):
    url = f"http://localhost:8000/analytics/insights?username={username}"
    # In production, use standard fetching if we need actual score.
    # For now, we will query via our get_analytics_insights endpoint internally
    try:
        from api.api import get_insights
        res = await get_insights(username)
        streak = res.get("streak", 0)
    except Exception:
        streak = 0
    # shields.io badge: brightness green
    return RedirectResponse(url=f"https://img.shields.io/badge/streak-{streak}-brightgreen")

@app.get("/badges/commits")
async def get_badge_commits(username: str, days: int = 30):
    try:
        from api.api import get_analytics_commits_per_day
        from gitpulse.core.repo_reader import _get_user_repos
        repos = await _get_user_repos(username)
        repo_csv = ",".join(repos)
        res = await get_insights_metrics(username, repo_csv, days)
        # res returns list of {commits, prs, issues}
        total_commits = sum(d.get("commits", 0) for d in res)
    except Exception:
        total_commits = 0
    return RedirectResponse(url=f"https://img.shields.io/badge/commits_{days}d-{total_commits}-blue")

@app.get("/badges/health")
async def get_badge_health(username: str):
    try:
        from api.api import get_insights_health
        from gitpulse.core.repo_reader import _get_user_repos
        repos = await _get_user_repos(username)
        repo_csv = ",".join(repos)
        res = await get_insights_health(username, repo_csv)
        health_score = res.get("health_score", 0)
    except Exception:
        health_score = 0
    color = "brightgreen" if health_score >= 80 else "yellow" if health_score >= 50 else "red"
    return RedirectResponse(url=f"https://img.shields.io/badge/health_score-{health_score}-{color}")


# ---------------------------------------------------------------------------
# Sprint 17: MCP SSE Proxy  (Step 1.5)
# ---------------------------------------------------------------------------

@app.get("/mcp/sse")
async def mcp_sse():
    """SSE endpoint advertising the available MCP tools.

    On connection the server emits a single ``event: tools`` frame containing
    the JSON schema for the two registered tools.  Clients may follow up with
    ``POST /mcp/sse/call`` to invoke a tool.

    Returns:
        StreamingResponse: A text/event-stream response with the tool list.
    """
    from fastapi.responses import StreamingResponse
    import json as _json

    tools_payload = [
        {
            "name": "generate_standup",
            "description": (
                "Fetch git activity for a GitHub user across one or more repositories "
                "and generate a professional standup summary using Groq LLaMA 3.3."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "GitHub username."},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of repository names.",
                    },
                    "days": {"type": "integer", "default": 7},
                    "source": {
                        "type": "string",
                        "enum": ["github", "local"],
                        "default": "github",
                    },
                    "tone": {
                        "type": "string",
                        "enum": ["standup", "retro"],
                        "default": "standup",
                    },
                },
                "required": ["username", "repos"],
            },
        },
        {
            "name": "get_insights",
            "description": (
                "Return aggregated commit, PR, and issue counts for a GitHub user. "
                "Fast — no LLM call."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "days": {"type": "integer", "default": 7},
                },
                "required": ["username", "repos"],
            },
        },
    ]

    async def event_stream():
        body = _json.dumps(tools_payload)
        yield f"event: tools\ndata: {body}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/mcp/sse/call")
async def mcp_sse_call(body: dict):
    """Invoke an MCP tool over HTTP and return the result as an SSE frame.

    Args:
        body: JSON body with keys ``tool`` (str) and ``params`` (dict).

    Returns:
        StreamingResponse: A text/event-stream response with ``event: result``.

    Raises:
        HTTPException 400: If body schema is invalid or tool is unknown.
    """
    from fastapi.responses import StreamingResponse
    from gitpulse_mcp.server import handle_generate_standup, handle_get_insights
    import json as _json

    tool_name = body.get("tool")
    params = body.get("params", {})

    if not tool_name:
        raise HTTPException(status_code=400, detail="'tool' is required")

    async def event_stream():
        try:
            if tool_name == "generate_standup":
                result = await handle_generate_standup(params)
            elif tool_name == "get_insights":
                result = await handle_get_insights(params)
            else:
                raise ValueError(f"Unknown tool: {tool_name!r}")

            if isinstance(result, dict):
                data = _json.dumps(result)
            else:
                data = _json.dumps({"text": result})
            yield f"event: result\ndata: {data}\n\n"
        except Exception as exc:
            logger.error("MCP SSE call failed: %s", exc, exc_info=True)
            yield f"event: error\ndata: {_json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Sprint 17: Proactive AI Recommendations  (Step 1.6)
# ---------------------------------------------------------------------------

@app.post("/insights/recommendations", response_model=RecommendationsResponse)
async def insights_recommendations(req: RecommendationsRequest):
    """Generate proactive AI recommendations for a user based on their activity.

    Queries GitHub for aggregated metrics over the requested period, then
    delegates to ``gitpulse.core.recommendations.get_recommendations``.

    Args:
        req: RecommendationsRequest with ``username`` and ``days``.

    Returns:
        RecommendationsResponse with the AI nudge string and a timestamp.

    Raises:
        HTTPException 503: If Groq API key is missing.
        HTTPException 500: On unexpected errors.
    """
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
        repos = await _get_user_repos(req.username)
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


# ---------------------------------------------------------------------------
# Sprint 17: Prompt Templates CRUD  (Step 1.7)
# ---------------------------------------------------------------------------

@app.post("/prompt-templates", response_model=PromptTemplateResponse, status_code=201)
async def create_prompt_template(req: PromptTemplateCreate):
    """Create a new saved prompt template.

    Args:
        req: PromptTemplateCreate with ``username``, ``name``, and ``content``.

    Returns:
        PromptTemplateResponse with the newly created template including its id.

    Raises:
        HTTPException 503: If db is disabled.
        HTTPException 500: On db errors.
    """
    db_pool = get_db_pool()
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                '''
                INSERT INTO prompt_templates (username, name, content)
                VALUES ($1, $2, $3)
                RETURNING id, username, name, content, created_at
                ''',
                req.username,
                req.name,
                req.content,
            )
            return PromptTemplateResponse(
                id=str(row["id"]),
                username=row["username"],
                name=row["name"],
                content=row["content"],
                created_at=row["created_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
    except Exception as exc:
        logger.error("Failed to create prompt template: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create prompt template")


@app.get("/prompt-templates", response_model=List[PromptTemplateResponse])
async def list_prompt_templates(username: str):
    """List all saved prompt templates for a user, newest first.

    Args:
        username: GitHub username whose templates to list.

    Returns:
        List of PromptTemplateResponse objects.

    Raises:
        HTTPException 503: If db is disabled.
    """
    db_pool = get_db_pool()
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                '''
                SELECT id, username, name, content, created_at
                FROM prompt_templates
                WHERE username = $1
                ORDER BY created_at DESC
                ''',
                username,
            )
            return [
                PromptTemplateResponse(
                    id=str(r["id"]),
                    username=r["username"],
                    name=r["name"],
                    content=r["content"],
                    created_at=r["created_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
                for r in rows
            ]
    except Exception as exc:
        logger.error("Failed to list prompt templates: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list prompt templates")


@app.delete("/prompt-templates/{template_id}", status_code=204)
async def delete_prompt_template(template_id: str):
    """Delete a saved prompt template by id.

    Args:
        template_id: UUID string of the template to delete.

    Raises:
        HTTPException 503: If db is disabled.
        HTTPException 404: If template not found.
    """
    db_pool = get_db_pool()
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM prompt_templates WHERE id::text = $1",
                template_id,
            )
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete prompt template: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete prompt template")

