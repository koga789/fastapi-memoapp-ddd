"""アプリケーション実行用"""

import logging

import anyio
from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.infrastructure.postgresql.db import async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5分間
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    """データベースの疎通を確認する（非同期）."""
    try:
        # 非同期セッションを使用して接続テスト
        async with async_session() as session:
            # SQLAlchemyのtextを使用してシンプルなクエリを実行
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise e


async def main() -> None:
    logger.info("Starting database connection check...")
    await init()
    logger.info("Database connection successful!")


if __name__ == "__main__":
    anyio.run(main, backend="asyncio")
