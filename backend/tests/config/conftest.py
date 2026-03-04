"""tests/config パッケージの共有フィクスチャ."""

import pytest

from app.config.app import AppSettings
from app.config.database import DatabaseSettings
from app.config.settings import Settings


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """テスト用の Settings インスタンスを生成するフィクスチャ.

    Returns:
        Settings: 必須環境変数を設定した Settings インスタンス
    """
    monkeypatch.setenv("PROJECT_NAME", "test-app")
    monkeypatch.setenv("PROJECT_DESCRIPTION", "A test description.")
    monkeypatch.setenv("POSTGRES_USER", "testuser")
    monkeypatch.setenv("POSTGRES_SERVER", "db.example.com")
    app = AppSettings(_env_file=None)  # type: ignore[call-arg]
    database = DatabaseSettings(_env_file=None)  # type: ignore[call-arg]
    return Settings(app=app, database=database)
