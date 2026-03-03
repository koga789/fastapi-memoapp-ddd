"""FindMemoByIdUseCaseのテスト."""

import pytest

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId
from app.usecase import FindMemoByIdUseCase


@pytest.mark.anyio
async def test_find_memo_by_id(
    find_memo_by_id_usecase: FindMemoByIdUseCase,
    mock_memo_repository: MemoRepository,
    sample_memo: Memo,
):
    """IDを指定してメモを取得できる."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = sample_memo

    # Act
    result = await find_memo_by_id_usecase.execute(memo_id=sample_memo.id)

    # Assert
    assert result == sample_memo
    assert result.id == sample_memo.id
    mock_memo_repository.find_by_id.assert_called_once_with(sample_memo.id)


@pytest.mark.anyio
async def test_find_memo_by_id_not_found(
    find_memo_by_id_usecase: FindMemoByIdUseCase,
    mock_memo_repository: MemoRepository,
):
    """存在しないIDを指定するとMemoNotFoundErrorが発生する."""
    # Arrange
    mock_memo_repository.find_by_id.return_value = None
    memo_id = MemoId.generate()

    # Act & Assert
    with pytest.raises(MemoNotFoundError):
        await find_memo_by_id_usecase.execute(memo_id=memo_id)

    mock_memo_repository.find_by_id.assert_called_once_with(memo_id)
