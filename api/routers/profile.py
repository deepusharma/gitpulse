"""Public profile router — no authentication required."""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from asyncpg.pool import Pool

from api.cache import analytics_cache
from api.db import get_db_pool
from api.dependencies import get_user_repos
from api.models import PublicProfileResponse
from api.utils import calculate_streak
from gitpulse.core.repo_reader import get_activity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])

_GITHUB_API = "https://api.github.com"


async def _fetch_github_user(username: str) -> dict:
    """Fetch basic GitHub user info (avatar_url, bio).

    Args:
        username: GitHub username to look up.

    Returns:
        Dict with at minimum 'avatar_url' and 'bio' keys.

    Raises:
        HTTPException: 404 if the user does not exist, 502 on network error.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{_GITHUB_API}/users/{username}",
                headers={"Accept": "application/vnd.github+json"},
            )
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
            resp.raise_for_status()
            return resp.json()
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Failed to fetch GitHub user %s: %s", username, exc, exc_info=True)
            raise HTTPException(status_code=502, detail="Failed to reach GitHub API")


async def _fetch_latest_public_summary(username: str, pool: Optional[Pool]) -> Optional[str]:
    """Return the most-recent public summary text for a user.

    Args:
        username: GitHub username.
        pool: Asyncpg connection pool (may be None if DB is unavailable).

    Returns:
        Summary text string, or None if no public summary exists.
    """
    if not pool:
        return None
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT summary FROM summaries
                WHERE username = $1 AND is_public = TRUE
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                username,
            )
            return row["summary"] if row else None
    except Exception as exc:
        logger.error("DB error fetching public summary for %s: %s", username, exc)
        return None


async def _fetch_total_summaries(username: str, pool: Optional[Pool]) -> int:
    """Return the total number of summaries stored for a user.

    Args:
        username: GitHub username.
        pool: Asyncpg connection pool.

    Returns:
        Integer count (0 on error or if DB unavailable).
    """
    if not pool:
        return 0
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM summaries WHERE username = $1",
                username,
            )
            return count or 0
    except Exception as exc:
        logger.error("DB error fetching summary count for %s: %s", username, exc)
        return 0


@router.get("/{username}", response_model=PublicProfileResponse)
async def get_public_profile(username: str, days: int = 30) -> PublicProfileResponse:
    """Return a public developer profile for the given GitHub username.

    No authentication required. Only public data is exposed:
    - GitHub avatar / bio
    - Commit streak derived from public repos
    - Top 5 repos by commit count (public only)
    - Latest public-flagged summary text
    - Health score and aggregate counts

    Args:
        username: GitHub username.
        days: Lookback window in days for activity metrics (default 30).

    Returns:
        PublicProfileResponse with all public profile fields.

    Raises:
        HTTPException: 404 if the user is not found on GitHub.
    """
    cache_key = f"profile:{username}:{days}"
    cached = analytics_cache.get(cache_key)
    if cached:
        logger.info("Profile cache hit for %s", username)
        return PublicProfileResponse(**cached)

    # 1. GitHub user info
    gh_user = await _fetch_github_user(username)
    avatar_url: str = gh_user.get("avatar_url", "")
    bio: Optional[str] = gh_user.get("bio")

    # 2. Public repos
    try:
        repos = await get_user_repos(username)
    except Exception:
        repos = []

    # 3. Activity → streak + top repos
    current_streak = 0
    longest_streak = 0
    top_repos: list[str] = []
    health_score = 0

    if repos:
        try:
            activity, _ = await get_activity(
                source="github", username=username, repos=repos, days=days
            )
            commits = activity.get("commits", [])

            # Streak
            date_set = {c["date"].date() for c in commits}
            current_streak, longest_streak = calculate_streak(list(date_set))

            # Top repos by commit count
            from collections import Counter  # noqa: PLC0415
            repo_counts = Counter(c["repo"] for c in commits)
            top_repos = [repo for repo, _ in repo_counts.most_common(5)]

            # Health score (best-effort)
            try:
                from api.routers.insights import get_insights_health  # noqa: PLC0415
                health_res = await get_insights_health(username, ",".join(repos))
                health_score = health_res.get("health_score", 0)
            except Exception as exc:
                logger.warning("Could not fetch health score for %s: %s", username, exc)

        except Exception as exc:
            logger.error("Activity fetch failed for profile %s: %s", username, exc)

    # 4. DB lookups
    pool = get_db_pool()
    recent_summary = await _fetch_latest_public_summary(username, pool)
    total_summaries = await _fetch_total_summaries(username, pool)

    result = PublicProfileResponse(
        username=username,
        avatar_url=avatar_url,
        bio=bio,
        recent_summary=recent_summary,
        current_streak=current_streak,
        longest_streak=longest_streak,
        top_repos=top_repos,
        health_score=health_score,
        total_summaries=total_summaries,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    # 5. Cache for 5 minutes
    analytics_cache.set(cache_key, result.model_dump(), ttl=300)

    return result
