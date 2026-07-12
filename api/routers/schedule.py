from fastapi import APIRouter, HTTPException, Depends
from api.models import DigestScheduleRequest, DigestScheduleResponse
from api.db import get_db_pool

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.post("", response_model=DigestScheduleResponse, status_code=201)
async def upsert_schedule(req: DigestScheduleRequest):
    if req.channel == "email" and not req.email_to:
        raise HTTPException(status_code=400, detail="email_to is required for email channel")
    if req.channel == "slack" and not req.slack_webhook:
        raise HTTPException(status_code=400, detail="slack_webhook is required for slack channel")
    if req.frequency == "weekly" and req.day_of_week is None:
        raise HTTPException(status_code=400, detail="day_of_week is required for weekly frequency")
        
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
        
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow('''
                INSERT INTO digest_schedules (
                    username, enabled, frequency, hour_utc, day_of_week, 
                    channel, email_to, slack_webhook, repos, days, tone, language
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (username) DO UPDATE SET
                    enabled = EXCLUDED.enabled,
                    frequency = EXCLUDED.frequency,
                    hour_utc = EXCLUDED.hour_utc,
                    day_of_week = EXCLUDED.day_of_week,
                    channel = EXCLUDED.channel,
                    email_to = EXCLUDED.email_to,
                    slack_webhook = EXCLUDED.slack_webhook,
                    repos = EXCLUDED.repos,
                    days = EXCLUDED.days,
                    tone = EXCLUDED.tone,
                    language = EXCLUDED.language,
                    updated_at = NOW()
                RETURNING id, username, enabled, frequency, hour_utc, day_of_week, 
                          channel, repos, days, last_sent_at, created_at
            ''', req.username, req.enabled, req.frequency, req.hour_utc, req.day_of_week,
                 req.channel, req.email_to, req.slack_webhook, req.repos, req.days,
                 req.tone, req.language)
            
            return DigestScheduleResponse(
                id=str(row['id']),
                username=row['username'],
                enabled=row['enabled'],
                frequency=row['frequency'],
                hour_utc=row['hour_utc'],
                day_of_week=row['day_of_week'],
                channel=row['channel'],
                repos=row['repos'],
                days=row['days'],
                last_sent_at=row['last_sent_at'].isoformat() if row['last_sent_at'] else None,
                created_at=row['created_at'].isoformat()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{username}", response_model=DigestScheduleResponse)
async def get_schedule(username: str):
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
        
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT id, username, enabled, frequency, hour_utc, day_of_week, 
                       channel, repos, days, last_sent_at, created_at
                FROM digest_schedules
                WHERE username = $1
            ''', username)
            
            if not row:
                raise HTTPException(status_code=404, detail="Schedule not found")
                
            return DigestScheduleResponse(
                id=str(row['id']),
                username=row['username'],
                enabled=row['enabled'],
                frequency=row['frequency'],
                hour_utc=row['hour_utc'],
                day_of_week=row['day_of_week'],
                channel=row['channel'],
                repos=row['repos'],
                days=row['days'],
                last_sent_at=row['last_sent_at'].isoformat() if row['last_sent_at'] else None,
                created_at=row['created_at'].isoformat()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{username}")
async def delete_schedule(username: str):
    pool = get_db_pool()
    if not pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
        
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM digest_schedules WHERE username = $1", username)
            return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
