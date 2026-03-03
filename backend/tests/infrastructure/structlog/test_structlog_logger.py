"""structlogロガー実装のユニットテスト."""

import structlog
from structlog.testing import LogCapture

from app.infrastructure.structlog import StructlogLogger, StructlogLoggerFactory
from app.usecase.interfaces import Logger, LoggerFactory


class TestStructlogLogger:
    """StructlogLoggerのテスト."""

    def test_implements_logger_interface(self) -> None:
        """StructlogLoggerがLoggerインターフェースを実装していることを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        assert isinstance(logger, Logger)

    def test_info_outputs_log(
        self,
        configure_test_logging: None,
        log_capture: LogCapture,
    ) -> None:
        """infoメソッドでログを出力できることを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        logger.info("test message", key="value")

        assert len(log_capture.entries) == 1
        assert log_capture.entries[0]["log_level"] == "info"  # LogCapture の仕様に合わせる
        assert log_capture.entries[0]["level"] == "INFO"  # 本番プロセッサの動作を検証
        assert log_capture.entries[0]["event"] == "test message"
        assert log_capture.entries[0]["key"] == "value"

    def test_all_log_levels_output(
        self,
        configure_test_logging: None,
        log_capture: LogCapture,
    ) -> None:
        """全てのログレベルでログを出力できることを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")

        assert len(log_capture.entries) == 5
        levels = [entry["log_level"] for entry in log_capture.entries]
        assert levels == ["debug", "info", "warning", "error", "critical"]

    def test_bind_adds_context(
        self,
        configure_test_logging: None,
        log_capture: LogCapture,
    ) -> None:
        """bindメソッドでコンテキストを追加できることを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        bound_logger_instance = logger.bind(user_id=123, request_id="abc")
        bound_logger_instance.info("log with context")

        assert len(log_capture.entries) == 1
        assert log_capture.entries[0]["user_id"] == 123
        assert log_capture.entries[0]["request_id"] == "abc"

    def test_bind_returns_new_logger_instance(
        self,
    ) -> None:
        """bindメソッドが新しいLoggerインスタンスを返すことを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        new_logger = logger.bind(key="value")

        assert new_logger is not logger
        assert isinstance(new_logger, Logger)

    def test_unbind_returns_new_logger_instance(
        self,
    ) -> None:
        """unbindメソッドが新しいLoggerインスタンスを返すことを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        bound_logger_instance = logger.bind(key="value")
        unbound_logger = bound_logger_instance.unbind("key")

        # インスタンスの同一性と型の確認
        assert unbound_logger is not bound_logger_instance
        assert isinstance(unbound_logger, Logger)

    def test_unbind_removes_context(
        self,
        configure_test_logging: None,
        log_capture: LogCapture,
    ) -> None:
        """unbindメソッドでバインド済みコンテキストが除去されることを確認."""
        bound_logger = structlog.get_logger(__name__)
        logger = StructlogLogger(bound_logger)

        bound = logger.bind(key="value")
        unbound = bound.unbind("key")
        unbound.info("after unbind")

        assert "key" not in log_capture.entries[0]


class TestStructlogLoggerFactory:
    """StructlogLoggerFactoryのテスト."""

    def test_implements_logger_factory_interface(self) -> None:
        """StructlogLoggerFactoryがLoggerFactoryインターフェースを実装していることを確認."""
        factory = StructlogLoggerFactory()

        assert isinstance(factory, LoggerFactory)

    def test_get_logger_returns_logger_instance(
        self,
    ) -> None:
        """get_loggerメソッドでLoggerインスタンスを取得できることを確認."""
        factory = StructlogLoggerFactory()

        logger = factory.get_logger(__name__)

        assert isinstance(logger, Logger)

    def test_get_logger_with_context(
        self,
        configure_test_logging: None,
        log_capture: LogCapture,
    ) -> None:
        """get_loggerメソッドでコンテキスト付きLoggerを取得できることを確認."""
        factory = StructlogLoggerFactory()

        logger = factory.get_logger(__name__, module="test", version="1.0")
        logger.info("test message")

        assert len(log_capture.entries) == 1
        assert log_capture.entries[0]["module"] == "test"
        assert log_capture.entries[0]["version"] == "1.0"

    def test_log_context_binds_temporarily(
        self,
        configure_test_logging: None,
        log_capture: LogCapture,
    ) -> None:
        """log_contextでコンテキスト内外でのログ出力を確認."""
        factory = StructlogLoggerFactory()
        logger = factory.get_logger(__name__)

        with factory.log_context(request_id="test-123"):
            logger.info("log inside context")

        logger.info("log outside context")

        assert len(log_capture.entries) == 2
        assert log_capture.entries[0]["request_id"] == "test-123"
        assert "request_id" not in log_capture.entries[1]
