"""メモの期限日の値オブジェクトを定義する."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class MemoDueDate:
    """メモの期限日を表現する値オブジェクト.

    Attributes:
        value: 期限日時（datetime）
        _skip_validation: バリデーションをスキップするかどうか（内部用）
    """

    value: datetime
    _skip_validation: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        """期限日のバリデーションを実行する.

        _skip_validation が True の場合、バリデーションをスキップする。
        これは永続化層からの復元時に使用される。

        Raises:
            ValueError: 期限日が過去の日時の場合（_skip_validation が False の場合のみ）
        """
        if self._skip_validation:
            return

        now = datetime.now(UTC) if self.value.tzinfo else datetime.now()
        if self.value < now:
            raise ValueError("Due date cannot be in the past")

    def __str__(self) -> str:
        """期限日のISO形式文字列を返す.

        Returns:
            str: ISO形式の日時文字列
        """
        return self.value.isoformat()

    @classmethod
    def create(cls, value: datetime) -> "MemoDueDate":
        """新しい期限日を作成するファクトリメソッド.

        ユーザー入力から期限日を作成する際に使用する。
        過去の日付は拒否される。

        Args:
            value: 期限日時

        Returns:
            MemoDueDate: 検証済みの期限日インスタンス

        Raises:
            ValueError: 期限日が過去の日時の場合
        """
        return cls(value=value, _skip_validation=False)

    @classmethod
    def reconstruct(cls, value: datetime) -> "MemoDueDate":
        """永続化されたデータから期限日を復元するファクトリメソッド.

        データベースからの読み込み時に使用する。
        バリデーションはスキップされる（保存時に検証済みのため）。

        Args:
            value: 期限日時

        Returns:
            MemoDueDate: 復元された期限日インスタンス
        """
        return cls(value=value, _skip_validation=True)
