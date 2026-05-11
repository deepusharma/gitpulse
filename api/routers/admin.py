"""Admin router — internal stats endpoint for GitPulse API."""

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks
from asyncpg.pool import Pool

from api.dependencies import get_db
from api.models import AdminStatsResponse
from api.worker import process_schedules

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def _verify_admin_token(x_admin_token: Optional[str] = Header(None)) -> None:
    """Verify the X-Admin-Token header against the ADMIN_TOKEN env var.

    Args:
        x_admin_token: Value of the X-Admin-Token request header.

    Raises:
        HTTPException: 403 if the token is missing or does not match.
    """
    expected = os.getenv("ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin endpoint not configured")
    if x_admin_token != expected:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(_verify_admin_token)])
async def get_admin_stats(
    days: int = 30,
    pool: Pool = Depends(get_db),
) -> AdminStatsResponse:
    """Return aggregate usage statistics for the GitPulse API.

    Auth-gated via X-Admin-Token header.

    Args:
        days: Lookback window for time-scoped metrics (default 30).
        pool: Injected asyncpg connection pool.

    Returns:
        AdminStatsResponse with counts and top repos.

    Raises:
        HTTPException: 500 on DB failure.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        async with pool.acquire() as conn:
            total_summaries: int = await conn.fetchval(
                "SELECT COUNT(*) FROM summaries"
            ) or 0

            unique_users: int = await conn.fetchval(
                "SELECT COUNT(DISTINCT username) FROM summaries"
            ) or 0

            summaries_last_n_days: int = await conn.fetchval(
                "SELECT COUNT(*) FROM summaries WHERE generated_at >= $1",
                since,
            ) or 0

            top_repo_rows = await conn.fetch(
                """
                SELECT repo, COUNT(*) AS cnt
                FROM summaries, UNNEST(repos) AS repo
                WHERE generated_at >= $1
                GROUP BY repo
                ORDER BY cnt DESC
                LIMIT 10
                """,
                since,
            )
            top_repos = [{"repo": r["repo"], "count": r["cnt"]} for r in top_repo_rows]

    except Exception as exc:
        logger.error("Admin stats DB query failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch admin stats")

    return AdminStatsResponse(
        total_summaries=total_summaries,
        unique_users=unique_users,
        summaries_last_n_days=summaries_last_n_days,
        top_repos=top_repos,
        error_rate_pct=0.0,  # placeholder — wire up request_logs in v1.7
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

@router.post("/trigger-worker", dependencies=[Depends(_verify_admin_token)])
async def trigger_worker(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_schedules)
    return {"ok": True, "message": "Worker triggered in background"}
