"""FindMemosUseCaseのテスト."""

import pytest

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoTitle
from app.usecase import FindMemosUseCase


@pytest.mark.anyio
async def test_find_all_memos(
    find_memos_usecase: FindMemosUseCase,
    mock_memo_repository: MemoRepository,
):
    """すべてのメモを取得できる."""
    # Arrange
    memo1 = Memo.create(title=MemoTitle("メモ1"))
    memo2 = Memo.create(title=MemoTitle("メモ2"))
    memo3 = Memo.create(title=MemoTitle("メモ3"))
    expected_memos = [memo1, memo2, memo3]
    mock_memo_repository.find_all.return_value = expected_memos

    # Act
    result = await find_memos_usecase.execute()

    # Assert
    assert len(result) == 3
    assert result == expected_memos
    mock_memo_repository.find_all.assert_called_once()


@pytest.mark.anyio
async def test_find_all_memos_empty(
    find_memos_usecase: FindMemosUseCase,
    mock_memo_repository: MemoRepository,
):
    """メモが存在しない場合は空のリストを返す."""
    # Arrange
    mock_memo_repository.find_all.return_value = []

    # Act
    result = await find_memos_usecase.execute()

    # Assert
    assert len(result) == 0
    assert result == []
    mock_memo_repository.find_all.assert_called_once()


@pytest.mark.anyio
async def test_find_all_memos_preserves_order(
    find_memos_usecase: FindMemosUseCase,
    mock_memo_repository: MemoRepository,
):
    """リポジトリが返す順序を保持する."""
    # Arrange
    memo1 = Memo.create(title=MemoTitle("メモ1"))
    memo2 = Memo.create(title=MemoTitle("メモ2"))
    expected_memos = [memo1, memo2]
    mock_memo_repository.find_all.return_value = expected_memos

    # Act
    result = await find_memos_usecase.execute()

    # Assert
    assert result[0] == memo1
    assert result[1] == memo2
    mock_memo_repository.find_all.assert_called_once()
