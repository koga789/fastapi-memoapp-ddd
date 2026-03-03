"""FastAPIアプリケーションのエントリポイント."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.structlog import setup_logging
from app.presentation.router import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """FastAPI の lifespan（ライフサイクル）を使用してアプリケーションの起動・終了処理を管理する.

    Yields:
        None: アプリケーションの実行期間
    """
    # アプリケーション起動時に structlog と stdlib logging の設定を初期化
    setup_logging()
    # yield より前が起動処理、yield より後がシャットダウン処理
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A RESTful API for managing memos using Domain-Driven Design principles.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # 許可するオリジンを指定
    allow_credentials=True,  # 認証情報を含むリクエストを許可
    allow_methods=["*"],  # 許可するHTTPメソッドを指定
    allow_headers=["*"],  # 許可するHTTPヘッダーを指定
)

# APIルーターをマウント
app.include_router(api_router)
