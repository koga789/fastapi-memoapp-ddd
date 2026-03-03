"""メモスキーマの変換テスト."""

from datetime import datetime, timedelta

from app.domain.entities import Memo
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoPriority,
    MemoTitle,
)
from app.presentation.schemas.memo import MemoResponseSchema


def test_memo_response_schema_from_entity():
    """ドメインエンティティからレスポンススキーマへの変換が正しく行われる."""
    # Arrange
    memo = Memo.create(
        title=MemoTitle("テストメモ"),
        description=MemoDescription("テスト用の説明"),
        priority=MemoPriority.HIGH,
        due_date=MemoDueDate(datetime.now() + timedelta(days=7)),
    )

    # Act
    schema = MemoResponseSchema.from_entity(memo)

    # Assert
    assert schema.id == str(memo.id.value)
    assert schema.title == memo.title.value
    assert schema.description == memo.description.value
    assert schema.priority == memo.priority.value
    assert schema.due_date == int(memo.due_date.value.timestamp() * 1000)
    assert schema.status == memo.status.value
    assert schema.created_at == int(memo.created_at.timestamp() * 1000)
    assert schema.updated_at == int(memo.updated_at.timestamp() * 1000)


def test_memo_response_schema_from_entity_with_none_optional_fields():
    """オプションフィールドがNoneの場合も正しく変換される."""
    # Arrange
    memo = Memo.create(
        title=MemoTitle("シンプルなメモ"),
        description=None,
        priority=MemoPriority.LOW,
        due_date=None,
    )

    # Act
    schema = MemoResponseSchema.from_entity(memo)

    # Assert
    assert schema.id == str(memo.id.value)
    assert schema.title == memo.title.value
    assert schema.description is None
    assert schema.priority == memo.priority.value
    assert schema.due_date is None
    assert schema.status == memo.status.value
    assert schema.created_at == int(memo.created_at.timestamp() * 1000)
    assert schema.updated_at == int(memo.updated_at.timestamp() * 1000)


def test_memo_response_schema_from_completed_entity():
    """完了済みメモのスキーマ変換が正しく行われる."""
    # Arrange
    memo = Memo.create(
        title=MemoTitle("完了済みメモ"),
        description=MemoDescription("完了したメモ"),
        priority=MemoPriority.MEDIUM,
    )
    memo.complete()

    # Act
    schema = MemoResponseSchema.from_entity(memo)

    # Assert
    assert schema.id == str(memo.id.value)
    assert schema.title == memo.title.value
    assert schema.status == "完了"
    assert memo.is_completed is True
