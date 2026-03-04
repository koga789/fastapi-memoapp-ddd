"""アプリケーション全体で使用する設定ファサードモジュール."""

from dataclasses import dataclass, field

from app.config.app import AppSettings
from app.config.database import DatabaseSettings


@dataclass
class Settings:
    """アプリケーション設定のファサードクラス.

    AppSettings と DatabaseSettings を統合し, 呼び出し元が単一の
    インターフェース（settings.xxx）で各設定値にアクセスできるようにする.
    """

    app: AppSettings = field(default_factory=AppSettings)  # type: ignore[arg-type]
    database: DatabaseSettings = field(default_factory=DatabaseSettings)  # type: ignore[arg-type]

    @property
    def project_name(self) -> str:
        """プロジェクト名を返す.

        Returns:
            str: AppSettings.project_name に委譲した値
        """
        return self.app.project_name

    @property
    def project_description(self) -> str:
        """プロジェクトの説明を返す.

        Returns:
            str: AppSettings.project_description に委譲した値
        """
        return self.app.project_description

    @property
    def api_v1_str(self) -> str:
        """API v1 のパスプレフィックスを返す.

        Returns:
            str: AppSettings.api_v1_str に委譲した値
        """
        return self.app.api_v1_str

    @property
    def environment(self) -> str:
        """実行環境を返す.

        Returns:
            str: AppSettings.environment に委譲した値
        """
        return self.app.environment

    @property
    def sqlalchemy_database_uri(self) -> str:
        """SQLAlchemy 用のデータベース接続 URI を文字列で返す.

        Returns:
            str: DatabaseSettings.sqlalchemy_database_uri を str に変換した値
        """
        return str(self.database.sqlalchemy_database_uri)


settings = Settings()
