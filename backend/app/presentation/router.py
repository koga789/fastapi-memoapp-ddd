"""FastAPIルーターの集約."""

from fastapi import APIRouter

from app.presentation.routes import health, memo

api_router = APIRouter(prefix="/api/v1")

# ヘルスチェックルートを登録
api_router.include_router(health.router)
# メモルートを登録
api_router.include_router(memo.router)
