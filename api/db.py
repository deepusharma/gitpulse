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
    except Exception as e:
        logger.error("Failed to initialize asyncpg pool: %s", e)

async def close_db():
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed.")

def get_db_pool():
    return pool
