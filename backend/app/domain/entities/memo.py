"""ドメイン層全体で使用するMemoエンティティを定義する."""

from datetime import datetime

from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoStatus,
    MemoTitle,
)


class Memo:
    """メモのドメインエンティティを表現する.

    Attributes:
        _id: メモの一意識別子
        _title: メモのタイトル
        _description: メモの詳細（任意）
        _priority: メモの優先度
        _due_date: メモの期限日（任意）
        _status: メモの完了状態
        _created_at: メモの作成日時
        _updated_at: メモの最終更新日時
    """

    def __init__(
        self,
        id: MemoId,
        title: MemoTitle,
        description: MemoDescription | None = None,
        priority: MemoPriority = MemoPriority.MEDIUM,
        due_date: MemoDueDate | None = None,
        status: MemoStatus = MemoStatus.INCOMPLETE,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        """メモのドメインエンティティを初期化する.

        Args:
            id: メモの識別子
            title: メモのタイトル
            description: メモの詳細（任意）
            priority: メモの優先度（デフォルト: MEDIUM）
            due_date: メモの期限日（任意）
            status: メモの完了状態（デフォルト: INCOMPLETE）
            created_at: 作成日時（UTC）
            updated_at: 最終更新日時（UTC）
        """
        self._id = id
        self._title = title
        self._description = description
        self._priority = priority
        self._due_date = due_date
        self._status = status
        self._created_at = created_at if created_at is not None else datetime.now()
        self._updated_at = updated_at if updated_at is not None else datetime.now()

    def __eq__(self, obj: object) -> bool:
        """メモの等価性を判定（IDベース）.

        Args:
            obj: 比較対象のオブジェクト

        Returns:
            bool: 同じIDを持つ場合True, それ以外はFalse
        """
        if isinstance(obj, Memo):
            return self.id == obj.id
        return False

    @property
    def id(self) -> MemoId:
        """メモの一意識別子を返す.

        Returns:
            MemoId: メモの識別子
        """
        return self._id

    @property
    def title(self) -> MemoTitle:
        """メモのタイトルを返す.

        Returns:
            MemoTitle: メモのタイトル
        """
        return self._title

    @property
    def description(self) -> MemoDescription | None:
        """メモの詳細を返す.

        Returns:
            MemoDescription | None: メモの詳細
        """
        return self._description

    @property
    def priority(self) -> MemoPriority:
        """メモの優先度を返す.

        Returns:
            MemoPriority: メモの優先度
        """
        return self._priority

    @property
    def due_date(self) -> MemoDueDate | None:
        """メモの期限日を返す.

        Returns:
            MemoDueDate | None: メモの期限日
        """
        return self._due_date

    @property
    def status(self) -> MemoStatus:
        """メモの完了状態を返す.

        Returns:
            MemoStatus: メモの完了状態
        """
        return self._status

    @property
    def created_at(self) -> datetime:
        """メモの作成日時を返す.

        Returns:
            datetime: メモの作成日時
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """メモの最終更新日時を返す.

        Returns:
            datetime: メモの最終更新日時
        """
        return self._updated_at

    def update_title(self, new_title: MemoTitle) -> None:
        """メモのタイトルを更新し, 更新日時を更新.

        Args:
            new_title: 新しいタイトル
        """
        self._title = new_title
        self._updated_at = datetime.now()

    def update_description(self, new_description: MemoDescription | None) -> None:
        """メモの詳細を更新し, 更新日時を更新.

        Args:
            new_description: 新しい詳細
        """
        self._description = new_description
        self._updated_at = datetime.now()

    def update_priority(self, new_priority: MemoPriority) -> None:
        """メモの優先度を更新し, 更新日時を更新.

        Args:
            new_priority: 新しい優先度
        """
        self._priority = new_priority
        self._updated_at = datetime.now()

    def update_due_date(self, new_due_date: MemoDueDate | None) -> None:
        """メモの期限日を更新し, 更新日時を更新.

        Args:
            new_due_date: 新しい期限日
        """
        self._due_date = new_due_date
        self._updated_at = datetime.now()

    def complete(self) -> None:
        """メモを完了状態にマークし, 更新日時を更新.

        Raises:
            ValueError: すでに完了状態の場合
        """
        if self._status == MemoStatus.COMPLETED:
            raise ValueError("Memo is already completed")
        self._status = MemoStatus.COMPLETED
        self._updated_at = datetime.now()

    def incomplete(self) -> None:
        """メモを未完了状態にマークし, 更新日時を更新."""
        self._status = MemoStatus.INCOMPLETE
        self._updated_at = datetime.now()

    @property
    def is_completed(self) -> bool:
        """メモが完了状態かどうかを返す.

        Returns:
            bool: 完了状態の場合True, それ以外はFalse
        """
        return self._status == MemoStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """メモが期限切れかどうかを判定.

        期限日が設定されていない場合, または完了済みの場合はFalse.
        現在時刻が期限日を過ぎている場合はTrue.

        Returns:
            bool: 期限切れの場合True, それ以外はFalse
        """
        if self.is_completed or self._due_date is None:
            return False
        return datetime.now() > self._due_date.value

    @staticmethod
    def create(
        title: MemoTitle,
        description: MemoDescription | None = None,
        priority: MemoPriority = MemoPriority.MEDIUM,
        due_date: MemoDueDate | None = None,
    ) -> "Memo":
        """新しいメモエンティティを生成するファクトリメソッド.

        Args:
            title: メモのタイトル
            description: メモの詳細（任意）
            priority: メモの優先度（デフォルト: MEDIUM）
            due_date: メモの期限日（任意）

        Returns:
            Memo: 新規作成されたメモインスタンス
        """
        return Memo(
            id=MemoId.generate(),
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
