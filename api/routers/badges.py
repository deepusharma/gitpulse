from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/badges", tags=["badges"])

@router.get("/streak")
async def get_badge_streak(username: str):
    # In production, use standard fetching if we need actual score.
    # For now, we will query via our get_analytics_insights endpoint internally
    try:
        from api.routers.analytics import get_insights
        res = await get_insights(username)
        streak = res.get("streak", 0)
    except Exception:
        streak = 0
    # shields.io badge: brightness green
    return RedirectResponse(url=f"https://img.shields.io/badge/streak-{streak}-brightgreen")

@router.get("/commits")
async def get_badge_commits(username: str, days: int = 30):
    try:
        from api.dependencies import get_user_repos
        from api.routers.insights import get_insights_metrics
        repos = await get_user_repos(username)
        repo_csv = ",".join(repos)
        res = await get_insights_metrics(username, repo_csv, days)
        # res returns list of {commits, prs, issues}
        total_commits = sum(d.get("commits", 0) for d in res)
    except Exception:
        total_commits = 0
    return RedirectResponse(url=f"https://img.shields.io/badge/commits_{days}d-{total_commits}-blue")

@router.get("/health")
async def get_badge_health(username: str):
    try:
        from api.dependencies import get_user_repos
        from api.routers.insights import get_insights_health
        repos = await get_user_repos(username)
        repo_csv = ",".join(repos)
        res = await get_insights_health(username, repo_csv)
        health_score = res.get("health_score", 0)
    except Exception:
        health_score = 0
    color = "brightgreen" if health_score >= 80 else "yellow" if health_score >= 50 else "red"
    return RedirectResponse(url=f"https://img.shields.io/badge/health_score-{health_score}-{color}")
