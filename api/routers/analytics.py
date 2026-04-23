from fastapi import APIRouter, HTTPException, Depends
from collections import Counter
from datetime import datetime, timezone, timedelta
import logging
from asyncpg.pool import Pool

from api.models import CompareResponse, CompareRecord
from api.dependencies import get_user_repos, get_db
from gitpulse.core.repo_reader import get_activity
from api.routers.insights import get_insights_health
from api.cache import analytics_cache

logger = logging.getLogger(__name__)

def calculate_streak(dates: list[datetime.date], ignore_weekends: bool = True) -> tuple[int, int]:
    """
    Calculate the current and longest streak from a list of dates.
    
    Returns:
        tuple[int, int]: (current_streak, longest_streak)
    """
    if not dates:
        return 0, 0
    
    sorted_dates = sorted(list(set(dates)), reverse=True)
    today = datetime.now(timezone.utc).date()
    
    # Calculate ALL streaks to find the longest one
    all_streaks = []
    if not sorted_dates:
        return 0, 0
        
    current_iter_streak = 1
    for i in range(len(sorted_dates) - 1):
        curr = sorted_dates[i]
        prev = sorted_dates[i+1]
        diff = (curr - prev).days
        
        is_consecutive = (diff == 1) or (ignore_weekends and curr.weekday() == 0 and prev.weekday() == 4 and diff == 3)
        
        if is_consecutive:
            current_iter_streak += 1
        else:
            all_streaks.append(current_iter_streak)
            current_iter_streak = 1
    all_streaks.append(current_iter_streak)
    
    longest_streak = max(all_streaks) if all_streaks else 0
    
    # Calculate CURRENT streak (must include today or yesterday)
    latest = sorted_dates[0]
    def is_recent(d1, d2):
        if d1 == d2: return True
        diff = (d1 - d2).days
        if diff == 1: return True
        if ignore_weekends:
            if d1.weekday() == 0 and d2.weekday() == 4 and diff == 3: return True
            if d1.weekday() == 6 and d2.weekday() == 4 and diff == 2: return True
            if d1.weekday() == 5 and d2.weekday() == 4 and diff == 1: return True
        return False

    if not is_recent(today, latest):
        current_streak = 0
    else:
        # The first streak in our all_streaks list (because we sorted descending)
        # IS the current streak IF it's recent.
        current_streak = all_streaks[0]
            
    return current_streak, longest_streak

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/compare", response_model=CompareResponse)
async def compare_periods(username: str, days: int = 30):
    """Compare performance metrics between current and previous periods."""
    repos = await get_user_repos(username)
    if not repos:
        raise HTTPException(status_code=404, detail="No repositories found for user")

    # Current period
    activity_curr, _ = await get_activity(source="github", username=username, repos=repos, days=days)
    
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

@router.get("/commits-per-day")
async def get_activity_per_day(username: str, days: int = 30):
    repos = await get_user_repos(username)
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

@router.get("/repos-breakdown")
async def get_repos_breakdown(username: str, days: int = 30):
    repos = await get_user_repos(username)
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

@router.get("/all")
async def get_analytics_full(
    username: str, 
    days: int = 30, 
    refresh: bool = False,
    pool: Pool = Depends(get_db)
):
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
    total_summaries = 0
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval('SELECT COUNT(*) FROM summaries')
            total_summaries = count or 0
    except Exception as e:
        logger.error("DB error figuring out summaries count: %s", e)
            
    # 2. Get user repos
    repos = await get_user_repos(username)
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
        
    # 4. Get health score
    health_score = 0
    try:
        health_res = await get_insights_health(username, ",".join(repos))
        health_score = health_res.get("health_score", 0)
    except Exception as e:
        logger.error("Failed to fetch health score for %s: %s", username, e)

    # 5. Process data (Frequency)
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
    
    streak, longest_streak = calculate_streak(list(date_set))
    
    average_commits = round(total_commits / days, 1)

    result = {
        "commits_per_day": commits_per_day,
        "repos_breakdown": repos_breakdown,
        "insights": {
            "most_active_day": most_active_day,
            "streak": streak,
            "longest_streak": longest_streak,
            "top_repo": top_repo,
            "total_summaries": total_summaries,
            "average_commits_per_day": average_commits,
            "health_score": health_score
        },
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Store in cache
    analytics_cache.set(cache_key, result, ttl=300)
    
    return result

@router.get("/insights")
async def get_insights(
    username: str, 
    days: int = 30,
    pool: Pool = Depends(get_db)
):
    # Get total summaries from DB
    total_summaries = 0
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval('SELECT COUNT(*) FROM summaries')
            total_summaries = count or 0
    except Exception as e:
        logger.error("DB error figuring out summaries count: %s", e)
            
    repos = await get_user_repos(username)
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
    
    streak, longest_streak = calculate_streak(list(date_set))
                
    average_commits = round(len(commits) / days, 1)
    
    return {
        "most_active_day": most_active_day,
        "streak": streak,
        "longest_streak": longest_streak,
        "top_repo": top_repo,
        "total_summaries": total_summaries,
        "average_commits_per_day": average_commits
    }
