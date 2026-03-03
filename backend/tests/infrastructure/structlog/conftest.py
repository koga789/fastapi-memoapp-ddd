"""インフラストラクチャ層（Structlog）のテスト用共通フィクスチャ."""

import logging
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
import structlog
from structlog.testing import LogCapture

from app.infrastructure.structlog import build_shared_processors


@pytest.fixture(autouse=True)
def _clear_log_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """テスト実行時に LOG_LEVEL / LOG_FORMAT 環境変数の影響を排除する."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("LOG_FORMAT", raising=False)


def _clean_logging_state() -> None:
    """structlog と標準 logging のグローバル状態をクリーンな初期状態に戻す."""
    # structlog のグローバル設定をデフォルト状態にリセット
    # structlog.configure() で設定したプロセッサチェーン、
    # ロガーファクトリ、キャッシュ設定がすべて初期状態に戻る
    structlog.reset_defaults()

    # 標準ライブラリ logging のルートロガーに登録されたハンドラをすべて除去
    # setup_logging() が addHandler() で追加したハンドラの蓄積を防止する
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # ログレベルを WARNING にリセット
    root_logger.setLevel(logging.WARNING)


@pytest.fixture
def log_capture() -> LogCapture:
    """テストで構造化ログをキャプチャするフィクスチャ.

    LogCapture は インメモリでログエントリ（`event_dict`）をキャプチャするための特殊なプロセッサ.
    プロセッサチェーンの末尾に配置することで、テスト時のみログ出力先をキャプチャに差し替える.
    log_capture.entries でキャプチャされたログエントリのリストを参照し、内容を検証できる.

    Examples:
        >>> def test_example(log_capture: LogCapture) -> None:
        ...     do_something()
        ...     assert log_capture.entries == [...]
    """
    return LogCapture()


@pytest.fixture
def configure_test_logging(log_capture: LogCapture) -> None:
    """LogCapture 付きでテスト用に structlog を設定するフィクスチャ.

    本番と同一のプロセッサチェーンを使用し、終端プロセッサのみ
    LogCapture に差し替える。本番のログ処理パイプラインをそのまま検証できる。

    Note:
        `cache_logger_on_first_use=False`: 生成済みのキャッシュロガーが reset_defaults() 後も残留し、
        再設定時に想定外の挙動を起こす可能性があるため、テストではキャッシュを無効化する。
        `filter_by_level`: テストで全レベルのログをキャプチャするため DEBUG を設定する。
    """
    processors = build_shared_processors()
    processors.append(log_capture)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )

    logging.root.setLevel(logging.DEBUG)


@pytest.fixture(autouse=True)
def _reset_logging():
    """各テスト前後に structlog と 標準 logging の設定をリセットするフィクスチャ.

    autouse=True により、すべてのテストに自動的に適用される.
    セットアップ・ティアダウンの両方でクリーンアップを実行し、
    他モジュールのテストによる状態汚染を防止する.
    """
    # 他モジュールのテストが structlog.configure() やルートロガーの設定変更を行った場合に備えてクリーンアップ
    _clean_logging_state()
    yield
    # 他モジュールのテストに影響を与えないよう、テスト完了後もクリーンアップを実行
    _clean_logging_state()


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """テスト用の一時ディレクトリを作成します.

    Yields:
        Path: 一時ディレクトリのパス

    Note:
        テスト完了後、一時ディレクトリは自動的に削除されます。
        このフィクスチャは各テスト関数ごとに実行されます。

    Examples:
        >>> def test_example(temp_dir: Path) -> None:
        ...     test_file = temp_dir / "test.txt"
        ...     test_file.write_text("test content")
        ...     assert test_file.exists()
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
