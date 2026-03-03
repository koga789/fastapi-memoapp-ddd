"""MemoDueDate値オブジェクトのテストケース."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.value_objects.memo_due_date import MemoDueDate


class TestMemoDueDateConstructor:
    """コンストラクタ直接呼び出しのテスト."""

    def test_create_valid_future_due_date(self):
        """未来の期限日が正しく作成できることをテストする."""
        future_date = datetime.now() + timedelta(days=7)
        due_date = MemoDueDate(future_date)
        assert due_date.value == future_date

    def test_create_past_due_date_raises_error(self):
        """過去の期限日を作成するとValueErrorが発生することをテストする."""
        past_date = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="Due date cannot be in the past"):
            MemoDueDate(past_date)

    def test_str_representation(self):
        """MemoDueDateの文字列表現がISO形式であることをテストする."""
        future_date = datetime.now() + timedelta(days=7)
        due_date = MemoDueDate(future_date)
        assert str(due_date) == future_date.isoformat()

    def test_due_date_equality(self):
        """MemoDueDateの等価性比較をテストする."""
        future_date_1 = datetime.now() + timedelta(days=7)
        future_date_2 = datetime.now() + timedelta(days=14)

        due_date_1a = MemoDueDate(future_date_1)
        due_date_1b = MemoDueDate(future_date_1)
        due_date_2 = MemoDueDate(future_date_2)

        assert due_date_1a == due_date_1b  # 同じ日時
        assert due_date_1a != due_date_2  # 異なる日時

    def test_due_date_immutability(self):
        """MemoDueDateが不変であることをテストする."""
        future_date = datetime.now() + timedelta(days=7)
        due_date = MemoDueDate(future_date)

        with pytest.raises(AttributeError):  # frozenクラスなので属性変更は不可
            due_date.value = datetime.now() + timedelta(days=14)


class TestMemoDueDateCreate:
    """create() ファクトリメソッドのテスト."""

    def test_create_with_future_date_succeeds(self):
        """未来の日付で作成できる."""
        future = datetime.now(UTC) + timedelta(days=1)
        due_date = MemoDueDate.create(future)
        assert due_date.value == future

    def test_create_with_past_date_raises_error(self):
        """過去の日付で作成するとエラーが発生する."""
        past = datetime.now(UTC) - timedelta(days=1)
        with pytest.raises(ValueError, match="Due date cannot be in the past"):
            MemoDueDate.create(past)

    def test_create_with_naive_datetime_succeeds(self):
        """タイムゾーン情報なしのdatetimeでも作成できる."""
        future = datetime.now() + timedelta(days=1)
        due_date = MemoDueDate.create(future)
        assert due_date.value == future


class TestMemoDueDateReconstruct:
    """reconstruct() ファクトリメソッドのテスト."""

    def test_reconstruct_with_past_date_succeeds(self):
        """過去の日付でも復元できる."""
        past = datetime.now(UTC) - timedelta(days=30)
        due_date = MemoDueDate.reconstruct(past)
        assert due_date.value == past

    def test_reconstruct_with_future_date_succeeds(self):
        """未来の日付でも復元できる."""
        future = datetime.now(UTC) + timedelta(days=1)
        due_date = MemoDueDate.reconstruct(future)
        assert due_date.value == future

    def test_reconstruct_skips_validation(self):
        """reconstruct()はバリデーションをスキップする."""
        very_old_date = datetime(2020, 1, 1, tzinfo=UTC)
        due_date = MemoDueDate.reconstruct(very_old_date)
        assert due_date.value == very_old_date


class TestMemoDueDateEquality:
    """create() と reconstruct() の等価性テスト."""

    def test_create_and_reconstruct_are_equal(self):
        """create() と reconstruct() で作成したインスタンスは等価."""
        future = datetime.now(UTC) + timedelta(days=1)
        created = MemoDueDate.create(future)
        reconstructed = MemoDueDate.reconstruct(future)
        assert created == reconstructed

    def test_skip_validation_flag_not_included_in_comparison(self):
        """_skip_validationフラグは等価性比較に含まれない."""
        future = datetime.now(UTC) + timedelta(days=1)
        with_validation = MemoDueDate(future, _skip_validation=False)
        without_validation = MemoDueDate(future, _skip_validation=True)
        assert with_validation == without_validation

    def test_skip_validation_flag_not_included_in_repr(self):
        """_skip_validationフラグはreprに含まれない."""
        future = datetime.now(UTC) + timedelta(days=1)
        due_date = MemoDueDate.create(future)
        repr_str = repr(due_date)
        assert "_skip_validation" not in repr_str
