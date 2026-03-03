"""ログ設定のユニットテスト."""

import json
import logging
from pathlib import Path

import pytest
import structlog

from app.infrastructure.structlog import set_log_level, setup_logging


class TestSetupLogging:
    """setup_logging関数のテスト."""

    def test_sets_log_level(self) -> None:
        """指定したログレベルが設定されることを確認."""
        # force=True でテスト間の設定を確実に上書き
        setup_logging(level="DEBUG", format="json", force=True)

        # ルートロガーのレベルが指定値に設定されていることを検証
        assert logging.root.level == logging.DEBUG

    def test_creates_log_file(self, temp_dir: Path) -> None:
        """ログファイルが作成されることを確認."""
        log_file = temp_dir / "subdir" / "test.log"

        setup_logging(level="INFO", format="json", log_file=log_file, force=True)

        # log_file が作成されることを検証
        assert log_file.exists()

    def test_json_format_outputs_valid_json(self, temp_dir: Path) -> None:
        """JSON形式でログが出力されることを確認."""
        log_file = temp_dir / "test.json"

        setup_logging(
            level="INFO",
            format="json",
            log_file=log_file,
            include_timestamp=True,
            include_caller_info=True,
            force=True,
        )

        # structlog.get_logger() で取得したロガーでログを出力
        logger = structlog.get_logger(__name__)
        logger.info("test message", test_key="test_value")

        assert log_file.exists()
        content = log_file.read_text().strip()

        # ファイルに出力されたログが有効な JSON であることを検証
        log_data = json.loads(content)
        assert log_data["event"] == "test message"
        assert log_data["test_key"] == "test_value"
        # ProcessorFormatter 経由でタイムスタンプとログレベルが付与されていることを検証
        assert "timestamp" in log_data
        assert "level" in log_data

    def test_env_variable_overrides_log_level(
        self,
        monkeypatch: pytest.MonkeyPatch,
        temp_dir: Path,
    ) -> None:
        """環境変数でログレベルが上書きされることを確認."""
        # LOG_LEVEL 環境変数が引数の level より優先されることを検証
        monkeypatch.setenv("LOG_LEVEL", "CRITICAL")

        log_file = temp_dir / "test.log"
        setup_logging(level="DEBUG", log_file=log_file, force=True)

        # 引数では DEBUG を指定したが、環境変数の CRITICAL が適用される
        assert logging.root.level == logging.CRITICAL

    def test_env_variable_overrides_log_format(
        self,
        monkeypatch: pytest.MonkeyPatch,
        temp_dir: Path,
    ) -> None:
        """環境変数でログフォーマットが上書きされることを確認."""
        # LOG_FORMAT 環境変数が引数の format より優先されることを検証
        monkeypatch.setenv("LOG_FORMAT", "json")

        log_file = temp_dir / "test.log"
        # 引数では console を指定したが、環境変数の json が適用される
        setup_logging(format="console", log_file=log_file, force=True)

        # ハンドラのフォーマッタが ProcessorFormatter であることを検証
        # （ProcessorFormatter はレンダラーを内包しており、JSON 出力を担う）
        handler = logging.root.handlers[0]
        assert isinstance(handler.formatter, structlog.stdlib.ProcessorFormatter)

    def test_skips_if_already_configured(self) -> None:
        """既に設定済みの場合はスキップされることを確認."""
        setup_logging(level="INFO", force=True)
        original_handlers = list(logging.root.handlers)

        # force=False（デフォルト）の場合、structlog.is_configured() が True を返すためスキップ
        setup_logging(level="DEBUG")

        # ログレベルもハンドラも変更されていないことを検証
        assert logging.root.level == logging.INFO
        assert logging.root.handlers == original_handlers

    def test_force_reconfigures(self) -> None:
        """force=True で再設定されることを確認."""
        setup_logging(level="INFO", force=True)

        # force=True を指定すると、is_configured() ガードを無視して再設定する
        setup_logging(level="DEBUG", force=True)

        assert logging.root.level == logging.DEBUG

    def test_stdlib_logger_uses_processor_formatter(self) -> None:
        """標準 logging のハンドラに ProcessorFormatter が設定されることを確認."""
        setup_logging(level="INFO", format="json", force=True)

        # ルートロガーのハンドラに ProcessorFormatter が設定されていることで、
        # stdlib logging 経由のログも structlog のプロセッサチェーンを通ることを検証
        handler = logging.root.handlers[0]
        assert isinstance(handler.formatter, structlog.stdlib.ProcessorFormatter)

    def test_stdlib_logger_outputs_structured_json(self, temp_dir: Path) -> None:
        """標準 logging 経由のログも構造化 JSON で出力されることを確認."""
        log_file = temp_dir / "test.json"
        setup_logging(
            level="INFO",
            format="json",
            log_file=log_file,
            include_timestamp=True,
            force=True,
        )

        # logging.getLogger() で取得した標準ロガーでログを出力
        # サードパーティライブラリ（uvicorn, SQLAlchemy 等）と同じ経路
        stdlib_logger = logging.getLogger("test.stdlib")
        stdlib_logger.info("stdlib message")

        content = log_file.read_text().strip()
        # stdlib 経由のログも foreign_pre_chain → ProcessorFormatter を通り、
        # 構造化 JSON として出力されていることを検証
        log_data = json.loads(content)
        assert log_data["event"] == "stdlib message"
        assert "timestamp" in log_data
        assert "level" in log_data


class TestSetLogLevel:
    """set_log_level関数のテスト."""

    def test_changes_root_logger_level(self) -> None:
        """ルートロガーのレベルが変更されることを確認."""
        setup_logging(level="INFO", force=True)

        # set_log_level() でルートロガーのレベルを動的に変更
        set_log_level("WARNING")

        assert logging.root.level == logging.WARNING

    def test_changes_specific_logger_level(self) -> None:
        """特定のロガーのレベルのみ変更されることを確認."""
        setup_logging(level="INFO", force=True)

        # logger_name を指定すると、そのロガーのみレベルを変更し、ルートロガーには影響しない
        set_log_level("DEBUG", logger_name="test.module")

        assert logging.getLogger("test.module").level == logging.DEBUG
        # ルートロガーのレベルは変更されていないことを検証
        assert logging.root.level == logging.INFO
