"""データベース接続設定を管理するモジュール."""

from typing import final

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class DatabaseSettings(BaseSettings):
    """データベース接続設定管理クラス.

    環境変数や .env ファイルから PostgreSQL 接続情報を読み込み,
    SQLAlchemy 用の接続 URI を構築する.
    """

    model_config = SettingsConfigDict(
        # トップレベルの .env ファイル（./backend/ の1つ上の階層）を参照する
        env_file="../.env",
        # 環境変数の値が空である場合、その値を無視し、クラス内で定義されているデフォルト値を採用する
        env_ignore_empty=True,
        # 定義されていない環境変数が .env にあっても、エラーにせず無視する
        extra="ignore",
    )
    postgres_user: str
    postgres_password: str = ""
    postgres_server: str
    postgres_port: int = 5432
    postgres_db: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        """SQLAlchemy 用のデータベース接続 URI を構築する.

        Returns:
            PostgresDsn: postgresql+psycopg スキームのデータベース接続 URI
        """
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            port=self.postgres_port,
            path=self.postgres_db,
        )
