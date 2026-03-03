"""MemoId値オブジェクトのテストケース."""

from uuid import UUID

import pytest

from app.domain.value_objects.memo_id import MemoId


class TestMemoIdGenerate:
    """generate() ファクトリメソッドのテスト."""

    def test_generate_creates_valid_uuid(self):
        """generate()が有効なUUIDを生成することをテストする."""
        memo_id = MemoId.generate()
        assert isinstance(memo_id.value, UUID)
        assert memo_id.value.version == 4

    def test_generate_creates_unique_ids(self):
        """generate()が一意のIDを生成することをテストする."""
        id1 = MemoId.generate()
        id2 = MemoId.generate()
        assert id1.value != id2.value


class TestMemoIdRepresentation:
    """文字列表現のテスト."""

    def test_str_representation(self):
        """MemoIdの文字列表現をテストする."""
        memo_id = MemoId.generate()
        assert str(memo_id) == str(memo_id.value)


class TestMemoIdEquality:
    """等価性のテスト."""

    def test_same_uuid_are_equal(self):
        """同じUUID値のMemoIdは等価である."""
        uuid_value = UUID("123e4567-e89b-12d3-a456-426614174000")
        id1 = MemoId(uuid_value)
        id2 = MemoId(uuid_value)
        assert id1 == id2

    def test_different_uuid_are_not_equal(self):
        """異なるUUID値のMemoIdは等価でない."""
        id1 = MemoId(UUID("123e4567-e89b-12d3-a456-426614174000"))
        id2 = MemoId.generate()
        assert id1 != id2


class TestMemoIdImmutability:
    """不変性のテスト."""

    def test_value_cannot_be_modified(self):
        """MemoIdが不変であることをテストする."""
        memo_id = MemoId.generate()

        with pytest.raises(AttributeError):
            memo_id.value = UUID("123e4567-e89b-12d3-a456-426614174000")
