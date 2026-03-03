"""structlogを使用したロガーの実装."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import structlog
from structlog import BoundLogger
from structlog.contextvars import bind_contextvars, unbind_contextvars

from app.usecase.interfaces.logger import Logger, LoggerFactory


class StructlogLogger(Logger):
    """structlogを使用したロガーの実装.

    structlog.BoundLoggerをラップし、Loggerインターフェースを実装する。
    """

    def __init__(self, logger: BoundLogger) -> None:
        """StructlogLoggerを初期化する.

        Args:
            logger: ラップするstructlogのBoundLoggerインスタンス
        """
        self._logger = logger

    def bind(self, **kwargs: Any) -> "StructlogLogger":
        """ロガーにコンテキスト変数をバインドする.

        Args:
            **kwargs: バインドするコンテキスト変数

        Returns:
            StructlogLogger: コンテキストがバインドされた新しいロガーインスタンス
        """
        return StructlogLogger(self._logger.bind(**kwargs))

    def unbind(self, *keys: str) -> "StructlogLogger":
        """ロガーからコンテキスト変数のバインドを解除する.

        Args:
            *keys: バインド解除するキー

        Returns:
            StructlogLogger: コンテキストが解除された新しいロガーインスタンス
        """
        return StructlogLogger(self._logger.unbind(*keys))

    def debug(self, event: str, **kwargs: Any) -> None:
        """デバッグメッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """
        self._logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        """情報メッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        """警告メッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        """エラーメッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """
        self._logger.error(event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        """致命的メッセージをログ出力する.

        Args:
            event: ログイベントメッセージ
            **kwargs: 追加のコンテキスト情報
        """
        self._logger.critical(event, **kwargs)


class StructlogLoggerFactory(LoggerFactory):
    """structlogを使用したロガーファクトリの実装."""

    def get_logger(self, name: str, **context: Any) -> Logger:
        """指定された名前とコンテキストでロガーを取得する.

        Args:
            name: ロガーの名前（通常は__name__）
            **context: ロガーにバインドする初期コンテキスト

        Returns:
            Logger: 設定済みロガーインスタンス
        """
        logger: BoundLogger = structlog.get_logger(name)
        if context:
            logger = logger.bind(**context)
        return StructlogLogger(logger)

    @contextmanager
    def log_context(self, **kwargs: Any) -> Iterator[None]:
        """コンテキスト変数を一時的にバインドするコンテキストマネージャ.

        Args:
            **kwargs: バインドするコンテキスト変数

        Yields:
            None: コンテキストマネージャのブロック内で使用
        """
        bind_contextvars(**kwargs)
        try:
            yield
        finally:
            unbind_contextvars(*kwargs.keys())
