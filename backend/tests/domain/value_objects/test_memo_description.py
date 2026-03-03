"""MemoDescription値オブジェクトのテストケース."""

import pytest

from app.domain.value_objects.memo_description import MemoDescription


class TestMemoDescriptionValidation:
    """バリデーションのテスト."""

    def test_create_valid_description(self):
        """有効な詳細が作成できることをテストする."""
        description = MemoDescription("テスト詳細")
        assert description.value == "テスト詳細"

    def test_create_empty_description(self):
        """空の詳細が作成できることをテストする."""
        description = MemoDescription("")
        assert description.value == ""

    def test_create_description_exceeding_length_limit(self):
        """255文字を超える詳細を作成するとValueErrorが発生することをテストする."""
        long_description = "あ" * 256
        with pytest.raises(ValueError, match="Description must be 255 characters or less"):
            MemoDescription(long_description)

    def test_description_exactly_255_characters(self):
        """ちょうど255文字の詳細が作成できることをテストする."""
        description_255 = "a" * 255
        description = MemoDescription(description_255)
        assert description.value == description_255


class TestMemoDescriptionRepresentation:
    """文字列表現のテスト."""

    def test_str_representation(self):
        """MemoDescriptionの文字列表現をテストする."""
        description = MemoDescription("テスト詳細")
        assert str(description) == "テスト詳細"


class TestMemoDescriptionEquality:
    """等価性のテスト."""

    def test_same_value_are_equal(self):
        """同じ値のMemoDescriptionは等価である."""
        desc1 = MemoDescription("同じ詳細")
        desc2 = MemoDescription("同じ詳細")
        assert desc1 == desc2

    def test_different_values_are_not_equal(self):
        """異なる値のMemoDescriptionは等価でない."""
        desc1 = MemoDescription("詳細1")
        desc2 = MemoDescription("詳細2")
        assert desc1 != desc2


class TestMemoDescriptionImmutability:
    """不変性のテスト."""

    def test_value_cannot_be_modified(self):
        """MemoDescriptionが不変であることをテストする."""
        description = MemoDescription("不変の詳細")

        with pytest.raises(AttributeError):
            description.value = "新しい詳細"
