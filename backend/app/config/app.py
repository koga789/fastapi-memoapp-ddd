"""アプリケーション固有の設定を管理するモジュール."""

from typing import Literal, final

from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class AppSettings(BaseSettings):
    """アプリケーション固有の設定管理クラス.

    環境変数や .env ファイルからアプリケーション名・APIパス・実行環境などの設定を読み込む.
    """

    model_config = SettingsConfigDict(
        # トップレベルの .env ファイル（./backend/ の1つ上の階層）を参照する
        env_file="../.env",
        # 環境変数の値が空である場合、その値を無視し、クラス内で定義されているデフォルト値を採用する
        env_ignore_empty=True,
        # 定義されていない環境変数が .env にあっても、エラーにせず無視する
        extra="ignore",
    )
    project_name: str
    project_description: str
    api_v1_str: str = "/api/v1"
    environment: Literal["local", "staging", "production"] = "local"
