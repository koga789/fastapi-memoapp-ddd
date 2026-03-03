"""Memoエンティティのテストケース."""

from datetime import datetime, timedelta

import pytest

from app.domain.entities.memo import Memo
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoStatus,
    MemoTitle,
)


class TestMemoCreation:
    """Memoエンティティの作成に関するテスト."""

    def test_create_memo_with_factory_method(self):
        """ファクトリメソッドでメモが作成できることをテストする."""
        title = MemoTitle("テストメモ")
        memo = Memo.create(title=title)

        assert memo.title == title
        assert memo.description is None
        assert memo.priority == MemoPriority.MEDIUM
        assert memo.due_date is None
        assert memo.status == MemoStatus.INCOMPLETE
        assert isinstance(memo.created_at, datetime)
        assert isinstance(memo.updated_at, datetime)

    def test_create_memo_with_all_parameters(self):
        """すべてのパラメータを指定してメモが作成できることをテストする."""
        title = MemoTitle("テストメモ")
        description = MemoDescription("詳細")
        due_date = MemoDueDate(datetime.now() + timedelta(days=7))

        memo = Memo.create(
            title=title,
            description=description,
            priority=MemoPriority.HIGH,
            due_date=due_date,
        )

        assert memo.title == title
        assert memo.description == description
        assert memo.priority == MemoPriority.HIGH
        assert memo.due_date == due_date
        assert memo.status == MemoStatus.INCOMPLETE

    def test_create_memo_with_constructor(self):
        """コンストラクタでメモが作成できることをテストする."""
        memo_id = MemoId.generate()
        title = MemoTitle("テストメモ")

        memo = Memo(id=memo_id, title=title)

        assert memo.id == memo_id
        assert memo.title == title
        assert memo.description is None
        assert memo.priority == MemoPriority.MEDIUM
        assert memo.status == MemoStatus.INCOMPLETE


class TestMemoProperties:
    """Memoエンティティのプロパティに関するテスト."""

    def test_all_property_accessors(self):
        """すべてのプロパティアクセサが正しく機能することをテストする."""
        memo_id = MemoId.generate()
        title = MemoTitle("テストメモ")
        description = MemoDescription("詳細")
        due_date = MemoDueDate(datetime.now() + timedelta(days=7))
        created_at = datetime.now()
        updated_at = datetime.now()

        memo = Memo(
            id=memo_id,
            title=title,
            description=description,
            priority=MemoPriority.HIGH,
            due_date=due_date,
            status=MemoStatus.INCOMPLETE,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert memo.id == memo_id
        assert memo.title == title
        assert memo.description == description
        assert memo.priority == MemoPriority.HIGH
        assert memo.due_date == due_date
        assert memo.status == MemoStatus.INCOMPLETE
        assert memo.created_at == created_at
        assert memo.updated_at == updated_at


class TestMemoUpdate:
    """Memoエンティティの更新に関するテスト."""

    def test_update_title(self):
        """タイトルが更新できることをテストする."""
        memo = Memo.create(title=MemoTitle("元のタイトル"))
        original_updated_at = memo.updated_at

        new_title = MemoTitle("新しいタイトル")
        memo.update_title(new_title)

        assert memo.title == new_title
        assert memo.updated_at > original_updated_at

    def test_update_description(self):
        """詳細が更新できることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))
        original_updated_at = memo.updated_at

        new_description = MemoDescription("新しい詳細")
        memo.update_description(new_description)

        assert memo.description == new_description
        assert memo.updated_at > original_updated_at

    def test_update_description_to_none(self):
        """詳細をNoneに更新できることをテストする."""
        memo = Memo.create(
            title=MemoTitle("テストメモ"),
            description=MemoDescription("元の詳細"),
        )

        memo.update_description(None)

        assert memo.description is None

    def test_update_priority(self):
        """優先度が更新できることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))
        original_updated_at = memo.updated_at

        memo.update_priority(MemoPriority.HIGH)

        assert memo.priority == MemoPriority.HIGH
        assert memo.updated_at > original_updated_at

    def test_update_due_date(self):
        """期限日が更新できることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))
        original_updated_at = memo.updated_at

        new_due_date = MemoDueDate(datetime.now() + timedelta(days=7))
        memo.update_due_date(new_due_date)

        assert memo.due_date == new_due_date
        assert memo.updated_at > original_updated_at

    def test_update_due_date_to_none(self):
        """期限日をNoneに更新できることをテストする."""
        memo = Memo.create(
            title=MemoTitle("テストメモ"),
            due_date=MemoDueDate(datetime.now() + timedelta(days=7)),
        )

        memo.update_due_date(None)

        assert memo.due_date is None


class TestMemoStatusTransition:
    """Memoエンティティの状態遷移に関するテスト."""

    def test_complete_memo(self):
        """メモを完了状態にできることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))
        original_updated_at = memo.updated_at

        memo.complete()

        assert memo.status == MemoStatus.COMPLETED
        assert memo.is_completed is True
        assert memo.updated_at > original_updated_at

    def test_complete_already_completed_memo_raises_error(self):
        """すでに完了状態のメモを完了状態にするとValueErrorが発生することをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))
        memo.complete()

        with pytest.raises(ValueError, match="Memo is already completed"):
            memo.complete()

    def test_incomplete_memo(self):
        """メモを未完了状態にできることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))
        memo.complete()

        memo.incomplete()

        assert memo.status == MemoStatus.INCOMPLETE
        assert memo.is_completed is False

    def test_incomplete_already_incomplete_memo(self):
        """未完了状態のメモを未完了状態にしてもエラーが発生しないことをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))

        memo.incomplete()  # すでに未完了だがエラーにならない

        assert memo.status == MemoStatus.INCOMPLETE


class TestMemoBusinessLogic:
    """Memoエンティティのビジネスロジックに関するテスト."""

    def test_is_completed_property(self):
        """is_completedプロパティが正しく機能することをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))

        assert memo.is_completed is False

        memo.complete()
        assert memo.is_completed is True

        memo.incomplete()
        assert memo.is_completed is False

    def test_is_overdue_with_future_due_date(self):
        """未来の期限日の場合, is_overdueがFalseになることをテストする."""
        memo = Memo.create(
            title=MemoTitle("テストメモ"),
            due_date=MemoDueDate(datetime.now() + timedelta(days=7)),
        )

        assert memo.is_overdue is False

    def test_is_overdue_without_due_date(self):
        """期限日が設定されていない場合, is_overdueがFalseになることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))

        assert memo.is_overdue is False

    def test_is_overdue_when_completed(self):
        """完了済みの場合, is_overdueがFalseになることをテストする."""
        memo_id = MemoId.generate()
        title = MemoTitle("テストメモ")
        due_date = MemoDueDate(datetime.now() + timedelta(days=7))

        memo = Memo(
            id=memo_id,
            title=title,
            due_date=due_date,
        )
        memo.complete()

        assert memo.is_overdue is False

    def test_is_overdue_with_past_due_date(self):
        """現在時刻が期限日を過ぎている場合, is_overdueがTrueになることをテストする."""
        memo_id = MemoId.generate()
        title = MemoTitle("テストメモ")
        past_date = datetime.now() - timedelta(days=1)
        due_date = MemoDueDate.__new__(MemoDueDate, past_date)
        object.__setattr__(due_date, "value", past_date)  # バリデーション回避

        memo = Memo(
            id=memo_id,
            title=title,
            due_date=due_date,
        )

        assert memo.is_overdue is True


class TestMemoEquality:
    """Memoエンティティの等価性比較に関するテスト."""

    def test_memo_equality_by_id(self):
        """同じIDを持つメモは等価であることをテストする."""
        memo_id = MemoId.generate()
        memo1 = Memo(id=memo_id, title=MemoTitle("メモ1"))
        memo2 = Memo(id=memo_id, title=MemoTitle("メモ2"))

        assert memo1 == memo2

    def test_memo_inequality_by_id(self):
        """異なるIDを持つメモは非等価であることをテストする."""
        memo1 = Memo.create(title=MemoTitle("メモ1"))
        memo2 = Memo.create(title=MemoTitle("メモ2"))

        assert memo1 != memo2

    def test_memo_inequality_with_non_memo_object(self):
        """メモと非メモオブジェクトは非等価であることをテストする."""
        memo = Memo.create(title=MemoTitle("テストメモ"))

        assert memo != "文字列"
        assert memo != 123
        assert memo is not None
