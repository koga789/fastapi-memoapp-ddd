"""PostgreSQL用MemoDTOの変換テスト."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.entities import Memo
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoStatus,
    MemoTitle,
)
from app.infrastructure.postgresql.memo.memo_dto import MemoDTO


class TestMemoDTOFromEntity:
    """from_entity() メソッドのテスト."""

    def test_from_entity_converts_memo_to_dto(self):
        """ドメインエンティティからDTOへの変換が正しく行われる."""
        # Arrange
        memo = Memo.create(
            title=MemoTitle("テストメモ"),
            description=MemoDescription("テスト用の説明"),
            priority=MemoPriority.HIGH,
            due_date=MemoDueDate.create(datetime.now(UTC) + timedelta(days=7)),
        )

        # Act
        memo_dto = MemoDTO.from_entity(memo)

        # Assert
        assert memo_dto.id == memo.id.value
        assert memo_dto.title == memo.title.value
        assert memo_dto.description == memo.description.value
        assert memo_dto.priority == memo.priority.value
        assert memo_dto.due_date == memo.due_date.value
        assert memo_dto.status == memo.status.value
        assert memo_dto.created_at == memo.created_at
        assert memo_dto.updated_at == memo.updated_at

    def test_from_entity_handles_none_optional_fields(self):
        """オプションフィールドがNoneの場合も正しく変換される."""
        # Arrange
        memo = Memo.create(
            title=MemoTitle("シンプルなメモ"),
            description=None,
            priority=MemoPriority.LOW,
            due_date=None,
        )

        # Act
        memo_dto = MemoDTO.from_entity(memo)

        # Assert
        assert memo_dto.id == memo.id.value
        assert memo_dto.title == memo.title.value
        assert memo_dto.description is None
        assert memo_dto.priority == memo.priority.value
        assert memo_dto.due_date is None
        assert memo_dto.status == memo.status.value


class TestMemoDTOToEntity:
    """to_entity() メソッドのテスト."""

    def test_to_entity_converts_dto_to_memo(self):
        """DTOからドメインエンティティへの変換が正しく行われる."""
        # Arrange
        memo_id = MemoId.generate()
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)
        due_date = datetime.now(UTC) + timedelta(days=7)

        memo_dto = MemoDTO(
            id=memo_id.value,
            title="テストメモ",
            description="テスト用の説明",
            priority="高",
            due_date=due_date,
            status="未完了",
            created_at=created_at,
            updated_at=updated_at,
        )

        # Act
        memo = memo_dto.to_entity()

        # Assert
        assert memo.id.value == memo_dto.id
        assert memo.title.value == memo_dto.title
        assert memo.description.value == memo_dto.description
        assert memo.priority.value == memo_dto.priority
        assert memo.due_date.value.timestamp() == pytest.approx(due_date.timestamp(), abs=0.001)
        assert memo.status == MemoStatus.INCOMPLETE
        assert memo.created_at.timestamp() == pytest.approx(created_at.timestamp(), abs=0.001)
        assert memo.updated_at.timestamp() == pytest.approx(updated_at.timestamp(), abs=0.001)

    def test_to_entity_handles_none_optional_fields(self):
        """オプションフィールドがNoneの場合も正しく変換される."""
        # Arrange
        memo_id = MemoId.generate()
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        memo_dto = MemoDTO(
            id=memo_id.value,
            title="シンプルなメモ",
            description=None,
            priority="低",
            due_date=None,
            status="完了",
            created_at=created_at,
            updated_at=updated_at,
        )

        # Act
        memo = memo_dto.to_entity()

        # Assert
        assert memo.id.value == memo_dto.id
        assert memo.title.value == memo_dto.title
        assert memo.description is None
        assert memo.priority == MemoPriority.LOW
        assert memo.due_date is None
        assert memo.status == MemoStatus.COMPLETED

    def test_to_entity_with_past_due_date_succeeds(self):
        """過去の期限日を持つDTOをエンティティに変換できる.

        reconstruct() を使用してバリデーションをスキップするため、
        過去の期限日でもエラーなく変換できる。
        """
        # Arrange
        memo_id = MemoId.generate()
        past_due_date = datetime.now(UTC) - timedelta(days=30)
        created_at = datetime.now(UTC) - timedelta(days=60)
        updated_at = datetime.now(UTC) - timedelta(days=30)

        memo_dto = MemoDTO(
            id=memo_id.value,
            title="過去の期限日を持つメモ",
            description="期限切れのメモ",
            priority="高",
            due_date=past_due_date,
            status="未完了",
            created_at=created_at,
            updated_at=updated_at,
        )

        # Act
        memo = memo_dto.to_entity()

        # Assert
        assert memo.due_date is not None
        assert memo.due_date.value < datetime.now(UTC)
        assert memo.due_date.value.timestamp() == pytest.approx(past_due_date.timestamp(), abs=0.001)

    def test_to_entity_with_very_old_due_date_succeeds(self):
        """非常に古い期限日を持つDTOでもエンティティに変換できる."""
        # Arrange
        memo_id = MemoId.generate()
        very_old_date = datetime(2020, 1, 1, tzinfo=UTC)
        created_at = datetime(2019, 12, 1, tzinfo=UTC)
        updated_at = datetime(2020, 1, 1, tzinfo=UTC)

        memo_dto = MemoDTO(
            id=memo_id.value,
            title="非常に古い期限日を持つメモ",
            description=None,
            priority="中",
            due_date=very_old_date,
            status="完了",
            created_at=created_at,
            updated_at=updated_at,
        )

        # Act
        memo = memo_dto.to_entity()

        # Assert
        assert memo.due_date is not None
        assert memo.due_date.value.year == 2020
        assert memo.due_date.value.month == 1
        assert memo.due_date.value.day == 1


class TestMemoDTORoundtrip:
    """往復変換のテスト."""

    def test_roundtrip_conversion_preserves_data(self):
        """エンティティ→DTO→エンティティの往復変換でデータが保持される."""
        # Arrange
        original_memo = Memo.create(
            title=MemoTitle("往復テスト"),
            description=MemoDescription("往復変換のテスト"),
            priority=MemoPriority.MEDIUM,
            due_date=MemoDueDate.create(datetime.now(UTC) + timedelta(days=7)),
        )

        # Act
        memo_dto = MemoDTO.from_entity(original_memo)
        converted_memo = memo_dto.to_entity()

        # Assert
        assert converted_memo.id == original_memo.id
        assert converted_memo.title.value == original_memo.title.value
        assert converted_memo.description.value == original_memo.description.value
        assert converted_memo.priority == original_memo.priority
        assert converted_memo.due_date.value.timestamp() == pytest.approx(
            original_memo.due_date.value.timestamp(), abs=0.001
        )
        assert converted_memo.status == original_memo.status

    def test_roundtrip_with_none_fields_preserves_data(self):
        """オプションフィールドがNoneの場合も往復変換でデータが保持される."""
        # Arrange
        original_memo = Memo.create(
            title=MemoTitle("シンプルな往復テスト"),
            description=None,
            priority=MemoPriority.LOW,
            due_date=None,
        )

        # Act
        memo_dto = MemoDTO.from_entity(original_memo)
        converted_memo = memo_dto.to_entity()

        # Assert
        assert converted_memo.id == original_memo.id
        assert converted_memo.title.value == original_memo.title.value
        assert converted_memo.description is None
        assert converted_memo.priority == original_memo.priority
        assert converted_memo.due_date is None
        assert converted_memo.status == original_memo.status
