"""PostgreSQL用MemoRepositoryの統合テスト.

PostgreSQL用のリポジトリ実装をテストする。
テストはトランザクション・ロールバック方式により各テスト後にDBをクリーンに保つ。
"""

from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoPriority,
    MemoStatus,
    MemoTitle,
)


@pytest.mark.anyio
async def test_save_and_find_by_id(memo_repository: MemoRepository, pg_test_session: AsyncSession):
    """メモを保存してIDで取得できる."""
    # Arrange
    memo = Memo.create(
        title=MemoTitle("テストメモ"),
        description=MemoDescription("テスト用の説明"),
        priority=MemoPriority.HIGH,
    )

    # Act
    await memo_repository.save(memo)
    await pg_test_session.flush()

    found_memo = await memo_repository.find_by_id(memo.id)

    # Assert
    assert found_memo is not None
    assert found_memo.id == memo.id
    assert found_memo.title.value == memo.title.value
    assert found_memo.description.value == memo.description.value
    assert found_memo.priority == memo.priority


@pytest.mark.anyio
async def test_find_by_id_returns_none_when_not_found(memo_repository: MemoRepository):
    """存在しないIDで検索するとNoneを返す."""
    # Arrange
    memo = Memo.create(title=MemoTitle("テストメモ"))

    # Act
    found_memo = await memo_repository.find_by_id(memo.id)

    # Assert
    assert found_memo is None


@pytest.mark.anyio
async def test_save_updates_existing_memo(memo_repository: MemoRepository, pg_test_session: AsyncSession):
    """既存のメモを更新できる."""
    # Arrange
    memo = Memo.create(
        title=MemoTitle("元のタイトル"),
        description=MemoDescription("元の説明"),
    )

    await memo_repository.save(memo)
    await pg_test_session.flush()

    # Act
    memo.update_title(MemoTitle("新しいタイトル"))
    memo.update_description(MemoDescription("新しい説明"))
    await memo_repository.save(memo)
    await pg_test_session.flush()

    found_memo = await memo_repository.find_by_id(memo.id)

    # Assert
    assert found_memo is not None
    assert found_memo.title.value == "新しいタイトル"
    assert found_memo.description.value == "新しい説明"


@pytest.mark.anyio
async def test_find_all_returns_all_memos(memo_repository: MemoRepository, pg_test_session: AsyncSession):
    """すべてのメモを取得できる."""
    # Arrange
    memo1 = Memo.create(title=MemoTitle("テストメモ1"))
    memo2 = Memo.create(title=MemoTitle("テストメモ2"))
    memo3 = Memo.create(title=MemoTitle("テストメモ3"))

    await memo_repository.save(memo1)
    await memo_repository.save(memo2)
    await memo_repository.save(memo3)
    await pg_test_session.flush()

    # Act
    memos = await memo_repository.find_all()

    # Assert
    assert len(memos) == 3
    memo_titles = {memo.title.value for memo in memos}
    assert memo_titles == {"テストメモ1", "テストメモ2", "テストメモ3"}


@pytest.mark.anyio
async def test_find_all_returns_empty_list_when_no_memos(memo_repository: MemoRepository):
    """メモが存在しない場合は空のリストを返す."""
    # Arrange

    # Act
    memos = await memo_repository.find_all()

    # Assert
    assert memos == []


@pytest.mark.anyio
async def test_find_all_returns_memos_in_descending_order(
    memo_repository: MemoRepository, pg_test_session: AsyncSession
):
    """メモは作成日時の降順で返される."""
    # Arrange

    memo1 = Memo.create(title=MemoTitle("最も古いメモ"))
    await memo_repository.save(memo1)
    await pg_test_session.flush()

    memo2 = Memo.create(title=MemoTitle("中間のメモ"))
    await memo_repository.save(memo2)
    await pg_test_session.flush()

    memo3 = Memo.create(title=MemoTitle("最新のメモ"))
    await memo_repository.save(memo3)
    await pg_test_session.flush()

    # Act
    memos = await memo_repository.find_all()

    # Assert
    assert len(memos) == 3
    assert memos[0].title.value == "最新のメモ"
    assert memos[1].title.value == "中間のメモ"
    assert memos[2].title.value == "最も古いメモ"


@pytest.mark.anyio
async def test_delete_removes_memo(memo_repository: MemoRepository, pg_test_session: AsyncSession):
    """メモを削除できる."""
    # Arrange
    memo = Memo.create(title=MemoTitle("削除対象のメモ"))

    await memo_repository.save(memo)
    await pg_test_session.flush()

    # Act
    await memo_repository.delete(memo.id)
    await pg_test_session.flush()

    found_memo = await memo_repository.find_by_id(memo.id)

    # Assert
    assert found_memo is None


@pytest.mark.anyio
async def test_save_preserves_all_memo_fields(memo_repository: MemoRepository, pg_test_session: AsyncSession):
    """すべてのメモフィールドが正しく保存される."""
    # Arrange
    due_date = MemoDueDate(datetime(2036, 1, 1, 10, 0, 0))
    memo = Memo.create(
        title=MemoTitle("完全なメモ"),
        description=MemoDescription("完全な説明"),
        priority=MemoPriority.HIGH,
        due_date=due_date,
    )
    memo.complete()

    # Act
    await memo_repository.save(memo)
    await pg_test_session.flush()

    found_memo = await memo_repository.find_by_id(memo.id)

    # Assert
    assert found_memo is not None
    assert found_memo.title.value == "完全なメモ"
    assert found_memo.description.value == "完全な説明"
    assert found_memo.priority == MemoPriority.HIGH
    assert found_memo.due_date is not None
    assert found_memo.status == MemoStatus.COMPLETED
    assert found_memo.is_completed is True
