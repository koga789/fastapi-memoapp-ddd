"""structlogを使用した構造化ログ設定."""

import inspect
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import structlog

type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
"""ログレベル型: Python標準ライブラリのログレベルに対応"""

type LogFormat = Literal["json", "console", "plain"]
"""ログフォーマット型:
- json: 構造化JSON出力（本番環境向け）
- console: カラフルで人間が読みやすい出力（開発環境向け）
- plain: シンプルなkey=value出力
"""


def add_caller_info(_: Any, __: Any, event_dict: dict[str, Any]) -> dict[str, Any]:
    """ログエントリに呼び出し元情報（ファイル、関数、行）を追加する.

    structlog プロセッサシグネチャに準拠する。
    第1引数（logger）・第2引数（method_name）は本プロセッサでは使用しない。
    Ref: https://www.structlog.org/en/stable/processors.html

    Args:
        _: structlog のロガーインスタンス（未使用）
        __: 呼び出されたログメソッド名（未使用）
        event_dict: ログイベント辞書。caller キーにファイル名・関数名・行番号を追加する

    Returns:
        caller 情報が追加されたイベント辞書
    """
    try:
        # inspect.stack() で完全なコールスタックを FrameInfo のリストとして取得
        stack = inspect.stack()

        # スタック全体を走査し、アプリケーションコードのフレームを特定する
        for f in stack:
            # フレームのグローバル名前空間から直接モジュール名を取得
            module_name = f.frame.f_globals.get("__name__", "")
            if (
                # structlog 内部のフレームをスキップ（プロセッサチェーンの呼び出し元）
                not module_name.startswith("structlog")
                # 標準ライブラリ logging のフレームをスキップ
                and not module_name.startswith("logging")
                # 本モジュール（ログ設定基盤）のフレームをスキップ
                and module_name != __name__
                # サードパーティライブラリのフレームをスキップ
                and "site-packages" not in f.filename
            ):
                # 最初に見つかったアプリケーションコードのフレームを呼び出し元として記録
                event_dict["caller"] = {
                    "filename": Path(f.filename).name,
                    "function": f.function,
                    "line": f.lineno,
                }
                break
    except Exception:  # nosec B110
        # フレーム取得に失敗してもログ出力を妨げない（ログパイプラインの安全性を優先）
        pass

    return event_dict


def add_timestamp(_: Any, __: Any, event_dict: dict[str, Any]) -> dict[str, Any]:
    """ログエントリにISOタイムスタンプを追加する."""
    event_dict["timestamp"] = datetime.now(UTC).isoformat()
    return event_dict


def add_log_level_upper(_: Any, __: Any, event_dict: dict[str, Any]) -> dict[str, Any]:
    """一貫性のためにログレベルを大文字に変換する."""
    if "level" in event_dict:
        event_dict["level"] = event_dict["level"].upper()
    return event_dict


def _select_renderer(format: LogFormat, is_local: bool) -> Any:
    """出力フォーマットに応じたレンダラーを選択する.

    Args:
        format: 出力フォーマット
        is_local: ローカル環境かどうか

    Returns:
        structlog のレンダラーインスタンス
    """
    if format == "json":
        # ログイベント辞書をJSON文字列に変換（ステージングや本番環境に最適）
        return structlog.processors.JSONRenderer()
    if format == "console" or is_local:
        try:
            # 色付きで読みやすいコンソール出力（開発環境に最適）
            return structlog.dev.ConsoleRenderer(colors=True)
        except ImportError:
            # rich ライブラリが利用できない場合は標準のコンソール出力にフォールバック
            return structlog.dev.ConsoleRenderer()
    # シンプルなkey=value形式の文字列で出力（色付けや特別な整形なし）
    return structlog.processors.KeyValueRenderer()


def build_shared_processors() -> list[Any]:
    """structlog プロセッサチェーンの共有部分を構築する.

    終端プロセッサ（wrap_for_formatter / LogCapture 等）を除く
    プロセッサ群を返す。本番設定とテスト設定の両方で使用し、
    プロセッサチェーンの一貫性を保証する。

    Returns:
        終端プロセッサを除くプロセッサのリスト
    """
    return [
        # 非同期タスクごとに独立したコンテキスト保持（プロセッサチェーンの最初に配置）
        # contextvars ベースでリクエストIDなどのスコープ情報をイベント辞書にマージする
        structlog.contextvars.merge_contextvars,
        # 標準ライブラリ logging のログレベルに基づいてイベントをフィルタリング
        structlog.stdlib.filter_by_level,
        # イベント辞書にロガー名を追加
        structlog.stdlib.add_logger_name,
        # イベント辞書にログレベルを追加
        structlog.stdlib.add_log_level,
        # ログメッセージ内の `%s` スタイルの位置引数を展開して追加
        structlog.stdlib.PositionalArgumentsFormatter(),
        # ログレベルを大文字に変換して追加（一貫性のため）
        add_log_level_upper,
        # スタックトレースをレンダリングして追加（デバッグに役立つ）
        structlog.processors.StackInfoRenderer(),
        # トレースバック付きの例外をレンダリングして追加（デバッグに役立つ）
        structlog.processors.format_exc_info,
    ]


def setup_logging(
    *,
    level: LogLevel | str = "INFO",
    format: LogFormat = "console",
    log_file: str | Path | None = None,
    include_timestamp: bool = True,
    include_caller_info: bool = True,
    force: bool = False,
) -> None:
    """構造化ログ設定をセットアップする.

    structlog と標準ライブラリ logging の両方を ProcessorFormatter で統合し、
    すべてのログ出力を同一のプロセッサチェーンとレンダラーで処理する。
    既に設定済みの場合は force=True を指定しない限りスキップする。

    Args:
        level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            - LOG_LEVEL環境変数でも設定可能
        format: 出力フォーマット: "json", "console", "plain"
            - json: 構造化JSON出力（本番環境に最適）
            - console: 色付き、人間が読みやすい出力（開発環境に最適）
            - plain: シンプルなkey=value出力
        log_file: ログを書き込むオプションのファイルパス
        include_timestamp: ログにISOタイムスタンプを追加するかどうか
        include_caller_info: 呼び出し元情報（ファイル、関数、行）を追加するかどうか
        force: 既に設定済みであっても強制的に再設定するかどうか
    """
    # 二重初期化防止: structlog.is_configured() は structlog.configure() が
    # 既に呼ばれたかどうかを返す。ハンドラの重複登録や設定の意図しない上書きを防ぐため、
    # 既に設定済みの場合は force=True を指定しない限り早期リターンする
    if structlog.is_configured() and not force:
        return

    # 環境変数からログレベルを取得（設定ファイルより環境変数を優先）
    env_level = os.environ.get("LOG_LEVEL", "").upper()
    if env_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        level = env_level

    # 環境変数からフォーマットを取得（設定ファイルより環境変数を優先）
    env_format = os.environ.get("LOG_FORMAT", "").lower()
    if env_format in ["json", "console", "plain"]:
        format = env_format  # noqa: A001

    # ── structlog 側のプロセッサチェーン ──
    # structlog.get_logger() 経由のログに適用されるプロセッサ群
    # 末尾の wrap_for_formatter がレンダラーの代わりに終端プロセッサとして機能し、
    # イベント辞書をレンダリングせずに ProcessorFormatter へ受け渡す
    structlog_processors = build_shared_processors()
    structlog_processors.append(
        # ── 終端プロセッサ ──
        # レンダラー（JSONRenderer 等）を直接配置する代わりに wrap_for_formatter を使用
        # イベント辞書を logging.LogRecord に格納し、ProcessorFormatter に委譲する
        # これにより structlog と 標準logging の出力を同一のプロセッサ群とレンダラーに統一できる
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    )

    # ── 標準logging 経由のログに適用する前処理チェーン（foreign_pre_chain） ──
    # logging.getLogger() で出力されるログ（uvicorn, SQLAlchemy 等のサードパーティ含む）は
    # structlog のプロセッサチェーンを通らないため、ProcessorFormatter が受け取った時点で
    # この前処理チェーンを適用し、structlog 側と同等のイベント辞書を構築する
    # 注意: filter_by_level は不要（標準logging 側で既にレベルフィルタリングが行われる）
    foreign_pre_chain = [p for p in build_shared_processors() if p is not structlog.stdlib.filter_by_level]

    # structlog のグローバル設定
    structlog.configure(
        # structlog.get_logger() 経由のログに適用するプロセッサチェーン
        processors=structlog_processors,
        # structlog が内部で使用するロガーファクトリ（logging の Logger を生成）
        logger_factory=structlog.stdlib.LoggerFactory(),
        # structlog のラッパークラス（.info(), .debug() 等のメソッドを提供）
        wrapper_class=structlog.stdlib.BoundLogger,
        # ロガーインスタンスをキャッシュしてパフォーマンスを向上（本番向け）
        cache_logger_on_first_use=True,
    )

    # ── ProcessorFormatter の構成 ──
    # structlog / 標準logging の両経路から来たログを統一的にレンダリングする
    # ProcessorFormatter は 標準logging の Formatter を継承しており、
    # ハンドラ（StreamHandler, FileHandler 等）のフォーマッタとして設定できる
    is_local = os.environ.get("ENVIRONMENT") == "local"
    renderer = _select_renderer(format, is_local)

    # ProcessorFormatter 内で適用するプロセッサ（レンダリング直前の最終処理）
    formatter_processors: list[Any] = [
        # structlog が内部的に付与したメタデータ（_record, _from_structlog 等）を除去
        # これらはイベント辞書の受け渡しに使用されるが、最終出力に含めたくないため
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    ]

    # 有効な場合はタイムスタンプを追加（ISO 8601 形式）
    if include_timestamp:
        formatter_processors.append(add_timestamp)
    # 有効な場合は呼び出し元情報（ファイル名、関数名、行番号）を追加
    if include_caller_info:
        formatter_processors.append(add_caller_info)

    # レンダラーを最後に配置する
    formatter_processors.append(renderer)

    formatter = structlog.stdlib.ProcessorFormatter(
        # 標準logging 経由のログに適用する前処理チェーン
        foreign_pre_chain=foreign_pre_chain,
        # structlog / 標準両経路のログに適用する最終処理チェーン（レンダラー含む）
        processors=formatter_processors,
    )

    # ── 標準ライブラリ logging のハンドラ設定 ──
    # ProcessorFormatter を設定したハンドラをルートロガーに登録する
    # これにより、すべてのログ（structlog / 標準問わず）が ProcessorFormatter を経由する
    root_logger = logging.getLogger()
    # 既存のハンドラをクリア（二重登録を防止）
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, level.upper()))

    # コンソール出力用ハンドラ（stdout に出力）
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # ファイル出力用ハンドラ（同じ ProcessorFormatter を使用し、構造化ログをファイルにも出力）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))
        # コンソールと同じ ProcessorFormatter を設定（出力形式を統一）
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # uvicorn が独自に登録するハンドラを除去し、ルートロガーへの伝播に一本化する
    # これにより uvicorn のログも ProcessorFormatter → foreign_pre_chain を経由して構造化される
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    # サードパーティライブラリのログレベル調整（冗長なログを抑制）
    if level != "DEBUG":
        for logger_name in ["uvicorn", "sqlalchemy", "httpx"]:
            logging.getLogger(logger_name).setLevel(logging.INFO)


def set_log_level(level: LogLevel | str, logger_name: str | None = None) -> None:
    """ログレベルを動的に変更する.

    Args:
        level: 新しいログレベル
        logger_name: 更新するロガーの名前。Noneの場合はルートロガーを更新
    """
    level_value = getattr(logging, level.upper())

    if logger_name:
        logging.getLogger(logger_name).setLevel(level_value)
    else:
        logging.root.setLevel(level_value)
        for handler in logging.root.handlers:
            handler.setLevel(level_value)
