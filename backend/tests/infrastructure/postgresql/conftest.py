"""インフラストラクチャ層（PostgreSQL）のテスト用共通フィクスチャ."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import MemoRepository
from app.infrastructure.postgresql.db import async_engine
from app.infrastructure.postgresql.memo.memo_repository import new_memo_repository


@pytest.fixture
async def pg_test_session() -> AsyncGenerator[AsyncSession]:
    """
    コンテキストマネージャーを使用してセッションとトランザクションを管理し、
    FastAPIのDIを安全に上書きするフィクスチャ。
    """
    # 1. DB接続を確立
    # この async with を抜ける際、session.close() と connection.close() が自動で実行される
    async with async_engine.connect() as connection:
        # 2. 外部トランザクションを開始
        async with connection.begin() as transaction:
            # 3. セッションをバインド
            async with AsyncSession(bind=connection, expire_on_commit=False) as session:
                try:
                    yield session
                    # ここで commit() が呼ばれても、外側の transaction がロールバックされるため安全
                finally:
                    # 4. 明示的にロールバック（beginコンテキストの終了時にも自動で行われるが、意図を明確化）
                    await transaction.rollback()


@pytest.fixture
def memo_repository(pg_test_session: AsyncSession) -> MemoRepository:
    """リポジトリの単体テスト、およびリポジトリが必要な他のテスト用"""
    return new_memo_repository(pg_test_session)
