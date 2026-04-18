from fastapi import APIRouter, HTTPException, Depends
import logging
from asyncpg.pool import Pool

from api.models import PublicSummaryResponse
from api.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/summary/public/{summary_id}", response_model=PublicSummaryResponse)
async def get_public_summary(
    summary_id: str,
    pool: Pool = Depends(get_db)
):
    """Fetch a public summary by ID without authentication."""
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
