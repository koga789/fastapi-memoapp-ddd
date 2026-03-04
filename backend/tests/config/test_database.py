"""DatabaseSettings のユニットテスト."""

import pytest

from app.config.database import DatabaseSettings


class TestDatabaseSettings:
    """DatabaseSettings のテスト."""

    def test_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """デフォルト値が正しく設定されることを確認."""
        # Arrange
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)  # デフォルト検証のため除去
        monkeypatch.delenv("POSTGRES_PORT", raising=False)      # デフォルト検証のため除去
        monkeypatch.delenv("POSTGRES_DB", raising=False)        # デフォルト検証のため除去

        # Act
        settings = DatabaseSettings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.postgres_port == 5432
        assert settings.postgres_password == ""
        assert settings.postgres_db == ""

    def test_sqlalchemy_database_uri_contains_connection_info(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """環境変数の接続情報が sqlalchemy_database_uri に反映されることを確認."""
        # Arrange
        monkeypatch.setenv("POSTGRES_USER", "mydbuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "mypassword")
        monkeypatch.setenv("POSTGRES_SERVER", "db.example.com")
        monkeypatch.setenv("POSTGRES_DB", "mydb")

        # Act
        settings = DatabaseSettings(_env_file=None)  # type: ignore[call-arg]
        uri = str(settings.sqlalchemy_database_uri)

        # Assert
        assert "mydbuser" in uri
        assert "mypassword" in uri
        assert "db.example.com" in uri
        assert "mydb" in uri
