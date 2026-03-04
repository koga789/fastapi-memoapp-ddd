"""Settings ファサードのユニットテスト."""

from app.config.settings import Settings


class TestSettings:
    """Settings ファサードのテスト."""

    def test_project_name_delegation(self, settings: Settings) -> None:
        """settings.project_name が app.project_name の値を返すことを確認."""
        # Act
        result = settings.project_name

        # Assert
        assert result == "test-app"

    def test_project_description_delegation(self, settings: Settings) -> None:
        """settings.project_description が app.project_description の値を返すことを確認."""
        # Act
        result = settings.project_description

        # Assert
        assert result == "A test description."

    def test_api_v1_str_delegation(self, settings: Settings) -> None:
        """settings.api_v1_str が app.api_v1_str の値を返すことを確認."""
        # Act
        result = settings.api_v1_str

        # Assert
        assert result == "/api/v1"

    def test_environment_delegation(self, settings: Settings) -> None:
        """settings.environment が app.environment の値を返すことを確認."""
        # Act
        result = settings.environment

        # Assert
        assert result == "local"

    def test_sqlalchemy_database_uri_delegation(self, settings: Settings) -> None:
        """settings.sqlalchemy_database_uri が database の接続情報を含む文字列を返すことを確認."""
        # Act
        uri = settings.sqlalchemy_database_uri

        # Assert
        assert "testuser" in uri
        assert "db.example.com" in uri
