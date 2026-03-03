"""ロガーのインターフェース定義.

ユースケース層がロギング機能を使用するための抽象化。
具体的なロギングライブラリ（structlog, logging等）への依存を排除する。
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


class Logger(ABC):
    """構造化ロガーの抽象クラス.

    ユースケース層からロギング機能を利用するためのインターフェース。
    実装はインフラストラクチャ層で提供される。
    """

    @abstractmethod
    def bind(self, **kwargs: Any) -> "Logger":
        """ロガーにコンテキスト変数をバインドする.

        Args:
            **kwargs: バインドするコンテキスト変数

        Returns:
            Logger: コンテキストがバインドされた新しいロガーインスタンス
        """

    @abstractmethod
    def unbind(self, *keys: str) -> "Logger":
        """ロガーからコンテキスト変数のバインドを解除する.

        Args:
            *keys: バインド解除するキー

        Returns:
            Logger: コンテキストが解除された新しいロガーインスタンス
        """

    @abstractmethod
    def debug(self, event: str, **kwargs: Any) -> None:
        """デバッグメッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """

    @abstractmethod
    def info(self, event: str, **kwargs: Any) -> None:
        """情報メッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """

    @abstractmethod
    def warning(self, event: str, **kwargs: Any) -> None:
        """警告メッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """

    @abstractmethod
    def error(self, event: str, **kwargs: Any) -> None:
        """エラーメッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """

    @abstractmethod
    def critical(self, event: str, **kwargs: Any) -> None:
        """致命的メッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """


class LoggerFactory(ABC):
    """ロガーファクトリの抽象クラス.

    名前付きロガーインスタンスを生成するためのインターフェース。
    """

    @abstractmethod
    def get_logger(self, name: str, **context: Any) -> Logger:
        """指定された名前とコンテキストでロガーを取得する.

        Args:
            name: ロガーの名前（通常は__name__）
            **context: ロガーにバインドする初期コンテキスト

        Returns:
            Logger: 設定済みロガーインスタンス
        """

    @abstractmethod
    @contextmanager
    def log_context(self, **kwargs: Any) -> Iterator[None]:
        """コンテキスト変数を一時的にバインドするコンテキストマネージャ.

        Args:
            **kwargs: バインドするコンテキスト変数

        Yields:
            None: コンテキストマネージャのブロック内で使用
        """
