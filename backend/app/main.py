"""FastAPIアプリケーションのエントリポイント."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.infrastructure.structlog import setup_logging
from app.presentation.router import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """FastAPI の lifespan（ライフサイクル）を使用してアプリケーションの起動・終了処理を管理する.

    Yields:
        None: アプリケーションの実行期間
    """
    # アプリケーション起動時に structlog と logging の設定を初期化
    setup_logging()
    # yield より前が起動処理, yield より後がシャットダウン処理
    yield


app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    lifespan=lifespan,
)

# APIルーターをマウント
app.include_router(api_router)
