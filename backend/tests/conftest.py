"""テストルートの共通フィクスチャ."""

import pytest


@pytest.fixture
def anyio_backend():
    """AnyIO が使用する非同期バックエンドを指定するフィクスチャ.

    SQLAlchemy asyncio および psycopg v3 が asyncio バックエンドを前提としているため
    "asyncio" に固定する.
    SQLAlchemy の Trio 対応が実現した場合に params=["asyncio", "trio"] への変更を検討する.
    """
    return "asyncio"
