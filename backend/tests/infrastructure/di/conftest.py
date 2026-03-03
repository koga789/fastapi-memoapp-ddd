"""DI 層のテスト用共通フィクスチャ."""

from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import MemoRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    """モック AsyncSession を提供するフィクスチャ.

    async with 構文で使用できるよう __aenter__ が自身を返すよう設定する.

    Returns:
        AsyncMock: モックされたデータベースセッション
    """
    session = AsyncMock(spec=AsyncSession)
    session.__aenter__.return_value = session
    return session


@pytest.fixture
def mock_memo_repository() -> AsyncMock:
    """モックメモリポジトリを提供するフィクスチャ.

    Returns:
        AsyncMock: モックされたメモリポジトリ
    """
    return AsyncMock(spec=MemoRepository)
