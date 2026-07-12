import asyncio
import os
import logging
from datetime import datetime, timezone, timedelta
import httpx

# If running directly, configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api.db import init_db, get_db_pool, close_db
from gitpulse.core.repo_reader import get_activity
from gitpulse.core.summarise import format_activity, to_prompt_str, to_display_str, build_prompt, summarise
from api.models import EmailDeliverRequest, SlackDeliverRequest
from api.routers.deliver import deliver_slack, deliver_email

async def process_schedules():
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        logger.error("GROQ_API_KEY not set, skipping all schedules")
        return

    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set, will skip email schedules")

    pool = get_db_pool()
    if not pool:
        logger.error("DB pool not initialized")
        return

    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_day = now.weekday() # 0 = Monday, 6 = Sunday

    try:
        async with pool.acquire() as conn:
            # Query enabled schedules
            schedules = await conn.fetch("SELECT * FROM digest_schedules WHERE enabled=TRUE")
            for schedule in schedules:
                try:
                    # check if due
                    if schedule['hour_utc'] != current_hour:
                        continue
                    if schedule['frequency'] == 'weekly' and schedule['day_of_week'] != current_day:
                        continue
                    
                    # guard against double-firing in same hour
                    if schedule['last_sent_at']:
                        time_since_last = now - schedule['last_sent_at']
                        if time_since_last < timedelta(minutes=50):
                            continue

                    # verify channel requirements
                    if schedule['channel'] == 'email' and not resend_key:
                        logger.warning("Skipping email schedule for %s due to missing RESEND_API_KEY", schedule['username'])
                        continue

                    logger.info("Processing schedule for user %s", schedule['username'])
                    
                    # Call get_activity
                    token = os.getenv("GITHUB_TOKEN")
                    activity, errors = await get_activity(
                        source="github",
                        username=schedule['username'],
                        repos=schedule['repos'],
                        days=schedule['days'],
                        token=token
                    )
                    
                    commits = activity.get("commits", [])
                    prs = activity.get("prs", [])
                    issues = activity.get("issues", [])
                    if not commits and not prs and not issues:
                        logger.info("No activity for %s, skipping digest", schedule['username'])
                        await conn.execute("UPDATE digest_schedules SET last_sent_at = NOW(), updated_at = NOW() WHERE id = $1", schedule['id'])
                        continue

                    formatted = format_activity(activity)
                    prompt_str = to_prompt_str(formatted)
                    prompt = build_prompt(prompt_str, tone=schedule['tone'], language=schedule['language'])
                    summary_text = await summarise(prompt)

                    if schedule['channel'] == 'email':
                        req = EmailDeliverRequest(to=schedule['email_to'], summary=summary_text)
                        await deliver_email(req)
                    elif schedule['channel'] == 'slack':
                        req = SlackDeliverRequest(summary=summary_text, webhook_url=schedule['slack_webhook'])
                        await deliver_slack(req)

                    # Update last_sent_at
                    await conn.execute("UPDATE digest_schedules SET last_sent_at = NOW(), updated_at = NOW() WHERE id = $1", schedule['id'])
                    logger.info("Successfully delivered digest for %s", schedule['username'])
                
                except Exception as e:
                    logger.error("Failed to process schedule for %s: %s", schedule['username'], e)
    except Exception as e:
        logger.error("Database error in worker: %s", e)

async def main():
    await init_db()
    try:
        await process_schedules()
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
