"""MemoTitle値オブジェクトのテストケース."""

import pytest

from app.domain.value_objects.memo_title import MemoTitle


class TestMemoTitleValidation:
    """バリデーションのテスト."""

    def test_create_valid_title(self):
        """有効なタイトルが作成できることをテストする."""
        title = MemoTitle("テストメモ")
        assert title.value == "テストメモ"

    def test_empty_title_raises_error(self):
        """空文字列でタイトルを作成するとValueErrorが発生することをテストする."""
        with pytest.raises(ValueError, match="Title is required"):
            MemoTitle("")

    def test_title_too_long_raises_error(self):
        """50文字を超えるタイトルを作成するとValueErrorが発生することをテストする."""
        long_title = "あ" * 51
        with pytest.raises(ValueError, match="Title must be 50 characters or less"):
            MemoTitle(long_title)

    def test_title_exactly_50_characters(self):
        """ちょうど50文字のタイトルが作成できることをテストする."""
        title_50 = "a" * 50
        title = MemoTitle(title_50)
        assert title.value == title_50


class TestMemoTitleRepresentation:
    """文字列表現のテスト."""

    def test_str_representation(self):
        """MemoTitleの文字列表現をテストする."""
        title = MemoTitle("テストメモ")
        assert str(title) == "テストメモ"


class TestMemoTitleEquality:
    """等価性のテスト."""

    def test_same_value_are_equal(self):
        """同じ値のMemoTitleは等価である."""
        title1 = MemoTitle("同じタイトル")
        title2 = MemoTitle("同じタイトル")
        assert title1 == title2

    def test_different_values_are_not_equal(self):
        """異なる値のMemoTitleは等価でない."""
        title1 = MemoTitle("タイトル1")
        title2 = MemoTitle("タイトル2")
        assert title1 != title2


class TestMemoTitleImmutability:
    """不変性のテスト."""

    def test_value_cannot_be_modified(self):
        """MemoTitleが不変であることをテストする."""
        title = MemoTitle("テストメモ")

        with pytest.raises(AttributeError):
            title.value = "新しいタイトル"
