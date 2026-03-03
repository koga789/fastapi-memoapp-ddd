"""メモの識別子の値オブジェクトを定義する."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MemoId:
    """メモの一意識別子を表現する値オブジェクト.

    Attributes:
        value: UUID形式の識別子
    """

    value: UUID

    @staticmethod
    def generate() -> "MemoId":
        """メモエンティティ用の新しい識別子を生成する.

        Returns:
            MemoId: 新規生成された識別子
        """
        return MemoId(uuid4())

    def __str__(self) -> str:
        """UUIDの文字列表現を返す.

        Returns:
            str: UUID文字列
        """
        return str(self.value)
