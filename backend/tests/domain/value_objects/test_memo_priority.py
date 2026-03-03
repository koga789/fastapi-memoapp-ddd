"""MemoPriority値オブジェクトのテストケース."""

from app.domain.value_objects.memo_priority import MemoPriority


class TestMemoPriorityValues:
    """列挙値のテスト."""

    def test_low_value(self):
        """低優先度の値が正しく定義されていることをテストする."""
        assert MemoPriority.LOW.value == "低"

    def test_medium_value(self):
        """中優先度の値が正しく定義されていることをテストする."""
        assert MemoPriority.MEDIUM.value == "中"

    def test_high_value(self):
        """高優先度の値が正しく定義されていることをテストする."""
        assert MemoPriority.HIGH.value == "高"


class TestMemoPriorityRepresentation:
    """文字列表現のテスト."""

    def test_low_str_representation(self):
        """MemoPriority.LOWの文字列表現をテストする."""
        assert str(MemoPriority.LOW) == "低"

    def test_medium_str_representation(self):
        """MemoPriority.MEDIUMの文字列表現をテストする."""
        assert str(MemoPriority.MEDIUM) == "中"

    def test_high_str_representation(self):
        """MemoPriority.HIGHの文字列表現をテストする."""
        assert str(MemoPriority.HIGH) == "高"


class TestMemoPriorityEquality:
    """等価性のテスト."""

    def test_same_priority_are_equal(self):
        """同じ優先度は等価である."""
        assert MemoPriority.LOW == MemoPriority.LOW
        assert MemoPriority.MEDIUM == MemoPriority.MEDIUM
        assert MemoPriority.HIGH == MemoPriority.HIGH

    def test_different_priority_are_not_equal(self):
        """異なる優先度は等価でない."""
        assert MemoPriority.LOW != MemoPriority.HIGH
        assert MemoPriority.LOW != MemoPriority.MEDIUM
        assert MemoPriority.MEDIUM != MemoPriority.HIGH


class TestMemoPriorityFromString:
    """文字列からの生成テスト."""

    def test_create_low_from_string(self):
        """文字列からMemoPriority.LOWを作成できる."""
        low = MemoPriority("低")
        assert low == MemoPriority.LOW

    def test_create_medium_from_string(self):
        """文字列からMemoPriority.MEDIUMを作成できる."""
        medium = MemoPriority("中")
        assert medium == MemoPriority.MEDIUM

    def test_create_high_from_string(self):
        """文字列からMemoPriority.HIGHを作成できる."""
        high = MemoPriority("高")
        assert high == MemoPriority.HIGH
