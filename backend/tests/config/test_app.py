"""AppSettings のユニットテスト."""

import pytest

from app.config.app import AppSettings


class TestAppSettings:
    """AppSettings のテスト."""

    def test_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """デフォルト値が正しく設定されることを確認."""
        # Arrange
        monkeypatch.setenv("PROJECT_NAME", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.setenv("PROJECT_DESCRIPTION", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.delenv("API_V1_STR", raising=False)    # デフォルト検証のため除去
        monkeypatch.delenv("ENVIRONMENT", raising=False)   # デフォルト検証のため除去

        # Act
        settings = AppSettings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.api_v1_str == "/api/v1"
        assert settings.environment == "local"

    def test_project_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PROJECT_NAME 環境変数から読み込めることを確認."""
        # Arrange
        monkeypatch.setenv("PROJECT_NAME", "my-memo-app")
        monkeypatch.setenv("PROJECT_DESCRIPTION", "dummy")  # 必須フィールドの充足のみが目的

        # Act
        settings = AppSettings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.project_name == "my-memo-app"

    def test_project_description(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PROJECT_DESCRIPTION 環境変数から読み込めることを確認."""
        # Arrange
        monkeypatch.setenv("PROJECT_NAME", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.setenv("PROJECT_DESCRIPTION", "A memo management API.")

        # Act
        settings = AppSettings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.project_description == "A memo management API."

    def test_environment_staging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ENVIRONMENT=staging で staging になることを確認."""
        # Arrange
        monkeypatch.setenv("PROJECT_NAME", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.setenv("PROJECT_DESCRIPTION", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.setenv("ENVIRONMENT", "staging")

        # Act
        settings = AppSettings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.environment == "staging"

    def test_environment_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ENVIRONMENT=production で production になることを確認."""
        # Arrange
        monkeypatch.setenv("PROJECT_NAME", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.setenv("PROJECT_DESCRIPTION", "dummy")  # 必須フィールドの充足のみが目的
        monkeypatch.setenv("ENVIRONMENT", "production")

        # Act
        settings = AppSettings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.environment == "production"
