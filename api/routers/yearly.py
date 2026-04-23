from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import logging
from asyncpg.pool import Pool
from collections import Counter

from api.dependencies import get_db
from gitpulse.core.summarise import summarise

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/year-in-review", tags=["analytics"])

@router.get("")
async def get_year_in_review(username: str, year: int = None, pool: Pool = Depends(get_db)):
    """
    Generate an annual Year in Review summary from history data.
    """
    if year is None:
        year = datetime.now(timezone.utc).year
        
    try:
        async with pool.acquire() as conn:
            # Fetch all summaries for the user in the given year
            # We assume generated_at is stored in UTC
            rows = await conn.fetch(
                """
                SELECT generated_at, summary, repos 
                FROM summaries 
                WHERE username = $1 AND EXTRACT(YEAR FROM generated_at) = $2
                ORDER BY generated_at ASC
                """,
                username, year
            )
    except Exception as e:
        logger.error("Failed to fetch yearly data from DB: %s", e)
        raise HTTPException(status_code=500, detail="Database error")

    if not rows:
        raise HTTPException(status_code=404, detail=f"No activity found for {username} in {year}")

    # Aggregate stats
    total_summaries = len(rows)
    all_repos = []
    month_counts = Counter()
    
    for row in rows:
        all_repos.extend(row['repos'])
        month_str = row['generated_at'].strftime("%b")
        month_counts[month_str] += 1
        
    repo_counts = Counter(all_repos)
    top_repos = [{"name": name, "count": count} for name, count in repo_counts.most_common(5)]
    
    monthly_breakdown = [
        {"month": m, "count": month_counts[m]} 
        for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ]

    # Find busiest day
    day_counts = Counter()
    for row in rows:
        day_counts[row['generated_at'].date()] += 1
    busiest_day_date, busiest_day_count = day_counts.most_common(1)[0]

    # Generate AI Wrap-up
    # We take snippets of summaries to keep the prompt size manageable
    summary_concat = "\n---\n".join([row['summary'][:200] for row in rows[:50]]) # Limit to 50 summaries
    
    prompt = f"""
    Generate a professional and celebratory annual "Year in Review" summary for a developer named {username}.
    Here is a condensed log of their standup summaries for the year {year}:
    
    {summary_concat}
    
    Based on this, write a 2-3 paragraph 'Spotify Wrapped' style narrative highlighting their major achievements, 
    growth, and consistency. Focus on themes of impact and technical progress.
    """
    
    try:
        ai_wrap_up = await summarise(prompt)
    except Exception as e:
        logger.error("Failed to generate AI wrap-up: %s", e)
        ai_wrap_up = "Could not generate AI summary at this time."

    return {
        "username": username,
        "year": year,
        "total_stats": {
            "summaries": total_summaries,
            "unique_repos": len(repo_counts)
        },
        "top_repos": top_repos,
        "monthly_breakdown": monthly_breakdown,
        "busiest_day": {
            "date": busiest_day_date.strftime("%Y-%m-%d"),
            "count": busiest_day_count
        },
        "ai_wrap_up": ai_wrap_up
    }
