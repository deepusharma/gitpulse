import os
import asyncpg
import logging

logger = logging.getLogger(__name__)

pool = None

async def init_db():
    global pool
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.warning("DATABASE_URL not set in environment. DB integration disabled.")
        return

    try:
        # Require SSL as per Neon defaults
        pool = await asyncpg.create_pool(db_url, min_size=1, max_size=10, ssl="require")
        logger.info("Successfully initialized asyncpg connection pool.")
        
        # Initialize rosters table
        await init_rosters_table()
        # Migration: Add is_public to summaries
        await init_summaries_public_migration()
        # Initialize prompt_templates table
        await init_prompt_templates_table()
        # Opt-in: request log table (ENABLE_DB_LOG=true)
        if os.environ.get("ENABLE_DB_LOG", "false").lower() == "true":
            await init_request_log_table()
    except Exception as e:
        logger.error("Failed to initialize asyncpg pool: %s", e)

async def init_summaries_public_migration():
    global pool
    if not pool:
        return
    try:
        async with pool.acquire() as conn:
            # PostgreSQL 9.6+ supports IF NOT EXISTS for ADD COLUMN
            await conn.execute('''
                ALTER TABLE summaries ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
            ''')
            logger.info("Checked/migrated 'summaries' table for 'is_public' column.")
    except Exception as e:
        logger.error("Error migrating 'summaries' table: %s", e)


async def init_rosters_table():
    global pool
    if not pool:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS rosters (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL,
                    usernames TEXT[] NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            ''')
            logger.info("Checked/created 'rosters' table.")
    except Exception as e:
        logger.error("Error creating 'rosters' table: %s", e)

async def init_prompt_templates_table():
    """Create the prompt_templates table if it does not already exist.

    Idempotent — safe to call on every startup.
    """
    global pool
    if not pool:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username TEXT NOT NULL,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            ''')
            logger.info("Checked/created 'prompt_templates' table.")
    except Exception as e:
        logger.error("Error creating 'prompt_templates' table: %s", e)



async def init_request_log_table() -> None:
    """Create the request_logs table if it does not already exist.

    Only called when ENABLE_DB_LOG=true. Idempotent.
    """
    global pool
    if not pool:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS request_logs (
                    id          BIGSERIAL PRIMARY KEY,
                    path        TEXT NOT NULL,
                    method      TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    latency_ms  INTEGER NOT NULL,
                    username    TEXT,
                    logged_at   TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_request_logs_logged_at
                    ON request_logs(logged_at);
            ''')
            logger.info("Checked/created 'request_logs' table.")
    except Exception as e:
        logger.error("Error creating 'request_logs' table: %s", e)


async def close_db():
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed.")

def get_db_pool():
    return pool
