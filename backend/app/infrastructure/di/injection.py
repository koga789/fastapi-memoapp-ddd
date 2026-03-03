"""アプリケーションの依存性注入設定."""

from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import MemoRepository
from app.infrastructure.postgresql.db import async_session
from app.infrastructure.postgresql.memo.memo_repository import new_memo_repository
from app.infrastructure.structlog import StructlogLoggerFactory
from app.usecase import (
    CompleteMemoUseCase,
    CreateMemoUseCase,
    DeleteMemoUseCase,
    FindMemoByIdUseCase,
    FindMemosUseCase,
    UpdateMemoUseCase,
    new_complete_memo_usecase,
    new_create_memo_usecase,
    new_delete_memo_usecase,
    new_find_memo_by_id_usecase,
    new_find_memos_usecase,
    new_update_memo_usecase,
)
from app.usecase.interfaces import Logger, LoggerFactory


async def get_session() -> AsyncIterator[AsyncSession]:
    """リクエストハンドリング用の管理されたSQLAlchemyセッションをyieldする.

    Yields:
        AsyncSession: 自動コミットまたはロールバックを行うデータベースセッション

    Raises:
        Exception: データベースまたはアプリケーションのエラーをロールバック後に伝播
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_memo_repository(session: AsyncSession = Depends(get_session)) -> MemoRepository:
    """現在のセッションにバインドされたリポジトリインスタンスを提供する.

    Args:
        session: FastAPIが提供するアクティブなSQLAlchemyセッション

    Returns:
        MemoRepository: セッションで設定されたリポジトリ
    """
    return new_memo_repository(session)


def get_create_memo_usecase(
    memo_repository: MemoRepository = Depends(get_memo_repository),
) -> CreateMemoUseCase:
    """注入されたリポジトリを持つメモ作成ユースケースを提供する.

    Args:
        memo_repository: FastAPIが提供するリポジトリ依存関係

    Returns:
        CreateMemoUseCase: 設定済みのユースケース実装
    """
    return new_create_memo_usecase(memo_repository)


def get_update_memo_usecase(
    memo_repository: MemoRepository = Depends(get_memo_repository),
) -> UpdateMemoUseCase:
    """注入されたリポジトリを持つメモ更新ユースケースを提供する.

    Args:
        memo_repository: FastAPIが提供するリポジトリ依存関係

    Returns:
        UpdateMemoUseCase: 設定済みのユースケース実装
    """
    return new_update_memo_usecase(memo_repository)


def get_complete_memo_usecase(
    memo_repository: MemoRepository = Depends(get_memo_repository),
) -> CompleteMemoUseCase:
    """注入されたリポジトリを持つメモ完了ユースケースを提供する.

    Args:
        memo_repository: FastAPIが提供するリポジトリ依存関係

    Returns:
        CompleteMemoUseCase: 設定済みのユースケース実装
    """
    return new_complete_memo_usecase(memo_repository)


def get_find_memo_by_id_usecase(
    memo_repository: MemoRepository = Depends(get_memo_repository),
) -> FindMemoByIdUseCase:
    """注入されたリポジトリを持つメモ個別取得ユースケースを提供する.

    Args:
        memo_repository: FastAPIが提供するリポジトリ依存関係

    Returns:
        FindMemoByIdUseCase: 設定済みのユースケース実装
    """
    return new_find_memo_by_id_usecase(memo_repository)


def get_find_memos_usecase(
    memo_repository: MemoRepository = Depends(get_memo_repository),
) -> FindMemosUseCase:
    """注入されたリポジトリを持つメモ一覧取得ユースケースを提供する.

    Args:
        memo_repository: FastAPIが提供するリポジトリ依存関係

    Returns:
        FindMemosUseCase: 設定済みのユースケース実装
    """
    return new_find_memos_usecase(memo_repository)


def get_delete_memo_usecase(
    memo_repository: MemoRepository = Depends(get_memo_repository),
) -> DeleteMemoUseCase:
    """注入されたリポジトリを持つメモ削除ユースケースを提供する.

    Args:
        memo_repository: FastAPIが提供するリポジトリ依存関係

    Returns:
        DeleteMemoUseCase: 設定済みのユースケース実装
    """
    return new_delete_memo_usecase(memo_repository)


def get_logger_factory() -> LoggerFactory:
    """ロガーファクトリを提供する.

    Returns:
        LoggerFactory: structlogを使用したロガーファクトリ
    """
    return StructlogLoggerFactory()


def get_logger(
    name: str = "app",
    logger_factory: LoggerFactory = Depends(get_logger_factory),
) -> Logger:
    """ロガーインスタンスを提供する.

    Args:
        name: ロガーの名前
        logger_factory: ロガーファクトリ

    Returns:
        Logger: 設定済みロガーインスタンス
    """
    return logger_factory.get_logger(name)
