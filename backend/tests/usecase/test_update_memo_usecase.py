"""UpdateMemoUseCaseのテスト."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoTitle,
)
from app.usecase import UpdateMemoUseCase


@pytest.mark.anyio
async def test_update_memo_title(
    update_memo_usecase: UpdateMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """メモのタイトルを更新できる."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo
    new_title = MemoTitle("新しいタイトル")

    # Act
    result = await update_memo_usecase.execute(
        memo_id=sample_memo.id,
        title=new_title,
    )

    # Assert
    assert result.title == new_title
    assert result.description == sample_memo.description
    assert result.priority == sample_memo.priority
    mock_memo_repository.find_by_id.assert_called_once_with(sample_memo.id)
    mock_memo_repository.save.assert_called_once()


@pytest.mark.anyio
async def test_update_memo_all_fields(
    update_memo_usecase: UpdateMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """メモのすべてのフィールドを更新できる."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo
    new_title = MemoTitle("新しいタイトル")
    new_description = MemoDescription("新しい説明")
    new_priority = MemoPriority.HIGH
    future_date = datetime.now(UTC) + timedelta(days=7)
    new_due_date = MemoDueDate.create(future_date)

    # Act
    result = await update_memo_usecase.execute(
        memo_id=sample_memo.id,
        title=new_title,
        description=new_description,
        priority=new_priority,
        due_date=new_due_date,
    )

    # Assert
    assert result.title == new_title
    assert result.description == new_description
    assert result.priority == new_priority
    assert result.due_date == new_due_date
    mock_memo_repository.save.assert_called_once()


@pytest.mark.anyio
async def test_update_memo_partial_fields(
    update_memo_usecase: UpdateMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """メモの一部のフィールドのみを更新できる."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo
    new_priority = MemoPriority.LOW

    # Act
    result = await update_memo_usecase.execute(
        memo_id=sample_memo.id,
        priority=new_priority,
    )

    # Assert
    assert result.title == sample_memo.title
    assert result.description == sample_memo.description
    assert result.priority == new_priority
    mock_memo_repository.save.assert_called_once()


@pytest.mark.anyio
async def test_update_memo_not_found(
    update_memo_usecase: UpdateMemoUseCase,
    mock_memo_repository: MemoRepository,
):
    """存在しないメモを更新しようとするとMemoNotFoundErrorが発生する."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = None
    memo_id = MemoId.generate()
    new_title = MemoTitle("新しいタイトル")

    # Act & Assert
    with pytest.raises(MemoNotFoundError):
        await update_memo_usecase.execute(memo_id=memo_id, title=new_title)

    mock_memo_repository.save.assert_not_called()
