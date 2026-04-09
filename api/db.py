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
    except Exception as e:
        logger.error("Failed to initialize asyncpg pool: %s", e)

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

async def close_db():
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed.")

def get_db_pool():
    return pool
