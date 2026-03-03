"""CreateMemoUseCaseのテスト."""

from datetime import datetime, timedelta

import pytest

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoTitle,
)
from app.usecase import CreateMemoUseCase


@pytest.mark.anyio
async def test_create_memo_with_all_fields(
    create_memo_usecase: CreateMemoUseCase,
    mock_memo_repository: MemoRepository,
):
    """すべてのフィールドを指定してメモを作成できる."""
    # Arrange
    title = MemoTitle("会議の準備")
    description = MemoDescription("明日の会議で使用する資料を準備する")
    priority = MemoPriority.HIGH
    due_date = MemoDueDate(datetime.now() + timedelta(days=1))

    # Act
    result = await create_memo_usecase.execute(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
    )

    # Assert
    assert isinstance(result, Memo)
    assert result.title == title
    assert result.description == description
    assert result.priority == priority
    assert result.due_date == due_date
    mock_memo_repository.save.assert_called_once()


@pytest.mark.anyio
async def test_create_memo_with_minimum_fields(
    create_memo_usecase: CreateMemoUseCase,
    mock_memo_repository: MemoRepository,
):
    """最小限のフィールド（タイトルのみ）でメモを作成できる."""
    # Arrange
    title = MemoTitle("シンプルなメモ")

    # Act
    result = await create_memo_usecase.execute(title=title)

    # Assert
    assert isinstance(result, Memo)
    assert result.title == title
    assert result.description is None
    assert result.priority == MemoPriority.MEDIUM
    assert result.due_date is None
    mock_memo_repository.save.assert_called_once()


@pytest.mark.anyio
async def test_create_memo_generates_unique_id(
    create_memo_usecase: CreateMemoUseCase,
):
    """メモ作成時に一意なIDが生成される."""
    # Arrange
    title = MemoTitle("テストメモ")

    # Act
    result = await create_memo_usecase.execute(title=title)

    # Assert
    assert isinstance(result.id, MemoId)
    assert result.id.value is not None
