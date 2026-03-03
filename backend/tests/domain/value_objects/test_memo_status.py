"""MemoStatus値オブジェクトのテストケース."""

from app.domain.value_objects.memo_status import MemoStatus


class TestMemoStatusValues:
    """列挙値のテスト."""

    def test_incomplete_value(self):
        """未完了ステータスの値が正しく定義されていることをテストする."""
        assert MemoStatus.INCOMPLETE.value == "未完了"

    def test_completed_value(self):
        """完了ステータスの値が正しく定義されていることをテストする."""
        assert MemoStatus.COMPLETED.value == "完了"


class TestMemoStatusRepresentation:
    """文字列表現のテスト."""

    def test_incomplete_str_representation(self):
        """MemoStatus.INCOMPLETEの文字列表現をテストする."""
        assert str(MemoStatus.INCOMPLETE) == "未完了"

    def test_completed_str_representation(self):
        """MemoStatus.COMPLETEDの文字列表現をテストする."""
        assert str(MemoStatus.COMPLETED) == "完了"


class TestMemoStatusEquality:
    """等価性のテスト."""

    def test_same_status_are_equal(self):
        """同じステータスは等価である."""
        assert MemoStatus.INCOMPLETE == MemoStatus.INCOMPLETE
        assert MemoStatus.COMPLETED == MemoStatus.COMPLETED

    def test_different_status_are_not_equal(self):
        """異なるステータスは等価でない."""
        assert MemoStatus.INCOMPLETE != MemoStatus.COMPLETED


class TestMemoStatusFromString:
    """文字列からの生成テスト."""

    def test_create_incomplete_from_string(self):
        """文字列からMemoStatus.INCOMPLETEを作成できる."""
        incomplete = MemoStatus("未完了")
        assert incomplete == MemoStatus.INCOMPLETE

    def test_create_completed_from_string(self):
        """文字列からMemoStatus.COMPLETEDを作成できる."""
        completed = MemoStatus("完了")
        assert completed == MemoStatus.COMPLETED
