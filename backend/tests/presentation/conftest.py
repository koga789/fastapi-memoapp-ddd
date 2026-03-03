"""プレゼンテーション層のテスト用共通フィクスチャ."""

from collections.abc import AsyncGenerator, Callable
from unittest.mock import AsyncMock

import pytest
from app.infrastructure.di.injection import get_session
from app.infrastructure.postgresql.db import async_engine
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def integration_client() -> AsyncGenerator[AsyncClient]:
    """統合テスト用の非同期 HTTP クライアントフィクスチャ.

    実際のデータベースに接続し, テスト終了後にトランザクションをロールバックして
    テスト間の副作用を排除する.
    正常系, Pydantic バリデーションエラー（400/422）, MemoNotFoundError（404）,
    値オブジェクト生成の ValueError（400）を検証する統合テストで使用する.

    Yields:
        AsyncClient: DB セッションにバインドされた非同期 HTTP クライアント
    """

    async with async_engine.connect() as connection:
        async with connection.begin() as transaction:
            async with AsyncSession(bind=connection, expire_on_commit=False) as session:
                # アプリケーション側のDIをテスト用の非同期セッションに差し替え
                app.dependency_overrides[get_session] = lambda: session

                try:
                    # テスト用に非同期HTTPクライアントを返却
                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        yield client
                finally:
                    app.dependency_overrides.clear()
                    await transaction.rollback()


@pytest.fixture
async def unit_client() -> AsyncGenerator[AsyncClient]:
    """ユニットテスト用の非同期 HTTP クライアントフィクスチャ.

    DB に接続せず, ルートハンドラの例外ハンドリングのみを単体で検証することを目的とする.
    各テスト内で app.dependency_overrides[get_xxx_usecase] を設定してユースケースを
    モックに差し替え, 予期しない例外（500）やユースケースからの ValueError（400）をテストする.
    フィクスチャ終了時に dependency_overrides をクリアして後処理する.

    Yields:
        AsyncClient: dependency_overrides による差し替えが可能な非同期 HTTP クライアント
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def failing_usecase() -> Callable:
    """execute が例外を送出するユースケースを dependency_overrides に設定するフィクスチャ.

    呼び出すたびに AsyncMock を生成して指定の例外を side_effect に設定し,
    app.dependency_overrides に登録する.
    後処理は unit_client フィクスチャの dependency_overrides.clear() に委譲する.

    Returns:
        Callable[[Callable, Exception], AsyncMock]: 依存関数と例外を受け取り AsyncMock を返す設定関数
    """

    def _setup(dep_func: Callable, error: Exception) -> AsyncMock:
        mock = AsyncMock()
        mock.execute.side_effect = error
        app.dependency_overrides[dep_func] = lambda: mock
        return mock

    return _setup
