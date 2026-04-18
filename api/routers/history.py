from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from asyncpg.pool import Pool

from api.models import HistoryResponse, PublicToggleRequest, PublicToggleResponse
from api.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
async def get_history(
    username: str, 
    limit: int = 10, 
    search: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    pool: Pool = Depends(get_db)
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


@router.patch("/history/{summary_id}/public", response_model=PublicToggleResponse)
async def toggle_summary_public(
    summary_id: str, 
    req: PublicToggleRequest,
    pool: Pool = Depends(get_db)
):
    """Toggle the is_public flag for a summary."""
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
