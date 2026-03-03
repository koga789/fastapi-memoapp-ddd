"""app/di/injection.py のユニットテスト."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.infrastructure.di.injection import (
    get_complete_memo_usecase,
    get_create_memo_usecase,
    get_delete_memo_usecase,
    get_find_memo_by_id_usecase,
    get_find_memos_usecase,
    get_logger,
    get_logger_factory,
    get_memo_repository,
    get_session,
    get_update_memo_usecase,
)
from app.infrastructure.postgresql.memo.memo_repository import MemoRepositoryImpl
from app.infrastructure.structlog.structlog_logger import StructlogLoggerFactory
from app.usecase import (
    CompleteMemoUseCase,
    CreateMemoUseCase,
    DeleteMemoUseCase,
    FindMemoByIdUseCase,
    FindMemosUseCase,
    UpdateMemoUseCase,
)
from app.usecase.interfaces.logger import Logger, LoggerFactory
from sqlalchemy.ext.asyncio import AsyncSession

# ================================================================
# get_memo_repository
# ================================================================


def test_get_memo_repository_returns_memo_repository_impl(mock_session: AsyncMock):
    """get_memo_repository は MemoRepositoryImpl を返す."""
    # Arrange - mock_session はフィクスチャで提供

    # Act
    result = get_memo_repository(mock_session)

    # Assert
    assert isinstance(result, MemoRepositoryImpl)


# ================================================================
# get_create_memo_usecase
# ================================================================


def test_get_create_memo_usecase_returns_create_memo_usecase(
    mock_memo_repository: AsyncMock,
):
    """get_create_memo_usecase は CreateMemoUseCase を返す."""
    # Arrange - mock_memo_repository はフィクスチャで提供

    # Act
    result = get_create_memo_usecase(mock_memo_repository)

    # Assert
    assert isinstance(result, CreateMemoUseCase)


# ================================================================
# get_update_memo_usecase
# ================================================================


def test_get_update_memo_usecase_returns_update_memo_usecase(
    mock_memo_repository: AsyncMock,
):
    """get_update_memo_usecase は UpdateMemoUseCase を返す."""
    # Arrange - mock_memo_repository はフィクスチャで提供

    # Act
    result = get_update_memo_usecase(mock_memo_repository)

    # Assert
    assert isinstance(result, UpdateMemoUseCase)


# ================================================================
# get_complete_memo_usecase
# ================================================================


def test_get_complete_memo_usecase_returns_complete_memo_usecase(
    mock_memo_repository: AsyncMock,
):
    """get_complete_memo_usecase は CompleteMemoUseCase を返す."""
    # Arrange - mock_memo_repository はフィクスチャで提供

    # Act
    result = get_complete_memo_usecase(mock_memo_repository)

    # Assert
    assert isinstance(result, CompleteMemoUseCase)


# ================================================================
# get_find_memo_by_id_usecase
# ================================================================


def test_get_find_memo_by_id_usecase_returns_find_memo_by_id_usecase(
    mock_memo_repository: AsyncMock,
):
    """get_find_memo_by_id_usecase は FindMemoByIdUseCase を返す."""
    # Arrange - mock_memo_repository はフィクスチャで提供

    # Act
    result = get_find_memo_by_id_usecase(mock_memo_repository)

    # Assert
    assert isinstance(result, FindMemoByIdUseCase)


# ================================================================
# get_find_memos_usecase
# ================================================================


def test_get_find_memos_usecase_returns_find_memos_usecase(
    mock_memo_repository: AsyncMock,
):
    """get_find_memos_usecase は FindMemosUseCase を返す."""
    # Arrange - mock_memo_repository はフィクスチャで提供

    # Act
    result = get_find_memos_usecase(mock_memo_repository)

    # Assert
    assert isinstance(result, FindMemosUseCase)


# ================================================================
# get_delete_memo_usecase
# ================================================================


def test_get_delete_memo_usecase_returns_delete_memo_usecase(
    mock_memo_repository: AsyncMock,
):
    """get_delete_memo_usecase は DeleteMemoUseCase を返す."""
    # Arrange - mock_memo_repository はフィクスチャで提供

    # Act
    result = get_delete_memo_usecase(mock_memo_repository)

    # Assert
    assert isinstance(result, DeleteMemoUseCase)


# ================================================================
# get_logger_factory
# ================================================================


def test_get_logger_factory_returns_structlog_logger_factory():
    """get_logger_factory は StructlogLoggerFactory を返す."""
    # Act
    result = get_logger_factory()

    # Assert
    assert isinstance(result, StructlogLoggerFactory)


# ================================================================
# get_logger
# ================================================================


def test_get_logger_returns_logger_from_factory():
    """get_logger はファクトリから取得した Logger を返す."""
    # Arrange
    mock_logger = MagicMock(spec=Logger)
    mock_factory = MagicMock(spec=LoggerFactory)
    mock_factory.get_logger.return_value = mock_logger

    # Act
    result = get_logger(name="test", logger_factory=mock_factory)

    # Assert
    assert result is mock_logger
    mock_factory.get_logger.assert_called_once_with("test")


# ================================================================
# get_session
# ================================================================


@pytest.mark.anyio
async def test_get_session_yields_session(mock_session: AsyncMock):
    """get_session はセッションを yield する."""
    # Arrange
    with patch(
        "app.infrastructure.di.injection.async_session", return_value=mock_session
    ):
        # Act
        sessions: list[AsyncSession] = []
        async for session in get_session():
            sessions.append(session)

    # Assert
    assert len(sessions) == 1  # ジェネレータがちょうど1回だけ yield すること
    assert sessions[0] is mock_session  # yield された値が期待するオブジェクトであること


@pytest.mark.anyio
async def test_get_session_commits_on_success(mock_session: AsyncMock):
    """get_session は正常終了時にセッションをコミットする."""
    # Arrange
    with patch(
        "app.infrastructure.di.injection.async_session", return_value=mock_session
    ):
        # Act - 正常終了ケース
        async for _ in get_session():
            pass

    # Assert
    mock_session.commit.assert_called_once()  # 正常終了時にコミットされることを検証


@pytest.mark.anyio
async def test_get_session_rolls_back_on_exception(mock_session: AsyncMock):
    """get_session は例外発生時にセッションをロールバックする."""
    # Arrange
    with patch(
        "app.infrastructure.di.injection.async_session", return_value=mock_session
    ):
        gen = get_session()
        await gen.asend(None)  # ジェネレータを yield まで進める

        # Act
        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("DB error"))  # 例外をジェネレータ内に注入

    # Assert
    mock_session.rollback.assert_called_once()  # 例外発生時にロールバックされることを検証
    mock_session.commit.assert_not_called()  # 例外発生時にコミットされないことを検証


@pytest.mark.anyio
async def test_get_session_always_closes_session(mock_session: AsyncMock):
    """get_session は正常終了・例外発生を問わずセッションをクローズする."""
    # Arrange
    with patch(
        "app.infrastructure.di.injection.async_session", return_value=mock_session
    ):
        # Act - 正常終了ケース
        async for _ in get_session():
            pass

    # Assert
    mock_session.close.assert_called_once()  # 正常終了時にセッションがクローズされることを検証


@pytest.mark.anyio
async def test_get_session_closes_session_on_exception(mock_session: AsyncMock):
    """get_session は例外発生時もセッションをクローズする."""
    # Arrange
    with patch(
        "app.infrastructure.di.injection.async_session", return_value=mock_session
    ):
        gen = get_session()
        await gen.asend(None)  # ジェネレータを yield まで進める

        # Act
        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("DB error"))  # 例外をジェネレータ内に注入

    # Assert
    mock_session.close.assert_called_once()  # 例外発生時にセッションがクローズされることを検証
