"""ヘルスチェックエンドポイントのテスト."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(unit_client: AsyncClient):
    """ヘルスチェックエンドポイントが200とステータスを返す."""
    response = await unit_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
