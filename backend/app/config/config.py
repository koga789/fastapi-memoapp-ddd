from typing import Literal

from pydantic import (
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定管理クラス
    環境変数や .env ファイルから設定値を読み込み、アプリケーション全体で使用する設定を管理する。
    """

    model_config = SettingsConfigDict(
        # トップレベルの .env ファイル（./backend/ の1つ上の階層）を参照する
        env_file="../.env",
        # 環境変数の値が空である場合、その値を無視し、クラス内で定義されているデフォルト値を採用する
        env_ignore_empty=True,
        # 定義されていない環境変数が .env にあっても、エラーにせず無視する
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """SQLAlchemy用のデータベース接続URIを構築する.

        Returns:
            PostgresDsn: データベース接続URI
        """
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()  # type: ignore
