"""DeleteMemoUseCaseのテスト."""

import pytest

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId
from app.usecase import DeleteMemoUseCase


@pytest.mark.anyio
async def test_delete_memo(
    delete_memo_usecase: DeleteMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """メモを削除できる."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo

    # Act
    await delete_memo_usecase.execute(memo_id=sample_memo.id)

    # Assert
    mock_memo_repository.find_by_id.assert_called_once_with(sample_memo.id)
    mock_memo_repository.delete.assert_called_once_with(sample_memo.id)


@pytest.mark.anyio
async def test_delete_memo_not_found(
    delete_memo_usecase: DeleteMemoUseCase,
    mock_memo_repository: MemoRepository,
):
    """存在しないメモを削除しようとするとMemoNotFoundErrorが発生する."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = None
    memo_id = MemoId.generate()

    # Act & Assert
    with pytest.raises(MemoNotFoundError):
        await delete_memo_usecase.execute(memo_id=memo_id)

    mock_memo_repository.find_by_id.assert_called_once_with(memo_id)
    mock_memo_repository.delete.assert_not_called()


@pytest.mark.anyio
async def test_delete_memo_verifies_existence_before_deletion(
    delete_memo_usecase: DeleteMemoUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """削除前にメモの存在を確認する."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo

    # Act
    await delete_memo_usecase.execute(memo_id=sample_memo.id)

    # Assert
    # find_by_idがdeleteより先に呼ばれることを確認
    call_order = mock_memo_repository.method_calls
    assert call_order[0][0] == "find_by_id"
    assert call_order[1][0] == "delete"
