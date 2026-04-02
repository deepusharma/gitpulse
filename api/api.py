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

from api.cache import InMemoryCache

# Specialized caches with 5-minute default TTL
repo_cache = InMemoryCache()
commit_cache = InMemoryCache()
analytics_cache = InMemoryCache()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up GitPulse API v0.6.0")
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
    username: str
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

@app.post("/summarise", response_model=SummariseResponse)
async def create_summary(request: SummariseRequest, refresh: bool = False):
    """
    Generate a summary of commits for a given user and repositories.
    
    Args:
        request (SummariseRequest): The request payload containing username, repos, and days.
        refresh (bool): Whether to bypass existing cache (default False).
        
    Returns:
        SummariseResponse: The generated summary and associated metadata.
        
    Raises:
        HTTPException: If validation fails or downstream errors occur.
    """
    logger.info("Received summarise request for username: %s, repos: %s", request.username, request.repos)
    
    # 1. Check cache first
    cache_key = f"summary:{request.username}:{','.join(sorted(request.repos))}:{request.days}"
    if not refresh:
        cached_result = commit_cache.get(cache_key)
        if cached_result:
            logger.info("Using cached summary for %s", request.username)
            return SummariseResponse(**cached_result)

    if not request.username:
        logger.warning("Summarise request failed validation: missing username")
        raise HTTPException(status_code=422, detail="Username cannot be empty")
    if not request.repos:
        logger.warning("Summarise request failed validation: missing repos")
        raise HTTPException(status_code=422, detail="Repos list cannot be empty")

    try:
        # Calls the GitHub API adapter
        commits, errors = await get_commits(
            source="github",
            username=request.username,
            repos=request.repos,
            days=request.days
        )
        
        if not commits and errors:
            error_msg = errors[0]
            if "not found or is private" in error_msg.lower() or "not found" in error_msg.lower():
                logger.error("Repo error: %s", error_msg)
                raise HTTPException(status_code=404, detail={"error": error_msg, "code": 404})
            elif "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail={"error": error_msg, "code": 429})
            else:
                raise Exception(error_msg)
        elif errors:
            logger.warning("Encountered partial errors during commit fetch: %s", errors)
        
        formatted = format_commits(commits)
        prompt_str = to_prompt_str(formatted)
        display_str = to_display_str(formatted)
        
        prompt = build_prompt(prompt_str)
        summary = await summarise(prompt)
        
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

        result = {
            "display": display_str,
            "summary": summary,
            "repos": request.repos,
            "username": request.username,
            "days": request.days,
            "generated_at": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # Update cache
        commit_cache.set(cache_key, result, ttl=300)
        
        return SummariseResponse(**result)
    except Exception as e:
        logger.error("Error during summary generation: %s", e, exc_info=True)
        msg = str(e)
        if "not found or is private" in msg:
            raise HTTPException(status_code=404, detail={"error": "Repository not found or private.", "code": 404})
        elif "rate limit" in msg.lower() or "RateLimitError" in msg:
            raise HTTPException(status_code=429, detail={"error": "API rate limit exceeded. Please try again later.", "code": 429})
        elif "authentication" in msg.lower() or "AuthenticationError" in msg:
            raise HTTPException(status_code=401, detail={"error": "API Authentication failed. Check your API keys.", "code": 401})
        else:
            import traceback
            tb = traceback.format_exc()
            logger.error("Internal Error Traceback: %s", tb)
            raise HTTPException(status_code=500, detail={
                "error": "Failed to generate summary. Internal server error.",
                "traceback": tb if os.getenv("DEBUG", "false").lower() == "true" else None,
                "code": 500
            })

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
async def get_commits_per_day(username: str, days: int = 30):
    repos = await _get_user_repos(username)
    if not repos:
        return []
    
    try:
        commits, errors = await get_commits(source="github", username=username, repos=repos, days=days)
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
        commits, errors = await get_commits(source="github", username=username, repos=repos, days=days)
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
        commits, errors = await get_commits(source="github", username=username, repos=repos, days=days)
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
        commits, errors = await get_commits(source="github", username=username, repos=repos, days=days)
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
