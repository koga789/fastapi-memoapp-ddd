"""CompleteMemoUseCaseのテスト."""

import pytest

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId, MemoStatus
from app.usecase import CompleteMemoUseCase


@pytest.mark.anyio
async def test_complete_memo(
    complete_memo_usecase: CompleteMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """メモを完了状態にできる."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo

    # Act
    result = await complete_memo_usecase.execute(memo_id=sample_memo.id)

    # Assert
    assert result.is_completed is True
    assert result.status == MemoStatus.COMPLETED
    mock_memo_repository.find_by_id.assert_called_once_with(sample_memo.id)
    mock_memo_repository.save.assert_called_once()


@pytest.mark.anyio
async def test_complete_memo_already_completed(
    complete_memo_usecase: CompleteMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """すでに完了しているメモを完了しようとするとエラーが発生する."""
    # Arrange
    sample_memo.complete()
    mock_memo_repository.find_by_id.return_value = sample_memo

    # Act & Assert
    with pytest.raises(ValueError, match="Memo is already completed"):
        await complete_memo_usecase.execute(memo_id=sample_memo.id)

    mock_memo_repository.save.assert_not_called()


@pytest.mark.anyio
async def test_complete_memo_not_found(
    complete_memo_usecase: CompleteMemoUseCase,
    mock_memo_repository: MemoRepository,
):
    """存在しないメモを完了しようとするとMemoNotFoundErrorが発生する."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = None
    memo_id = MemoId.generate()

    # Act & Assert
    with pytest.raises(MemoNotFoundError):
        await complete_memo_usecase.execute(memo_id=memo_id)

    mock_memo_repository.save.assert_not_called()
