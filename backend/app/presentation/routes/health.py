"""ヘルスチェック用のHTTPエンドポイント."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="ヘルスチェック",
    description="アプリケーションの稼働状態を確認します.",
)
async def health() -> dict[str, str]:
    """アプリケーションの稼働状態を返す.

    Returns:
        dict[str, str]: ステータスメッセージ
    """
    return {"status": "ok"}
