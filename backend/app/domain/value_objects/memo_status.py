"""メモの完了状態の列挙型を定義する."""

from enum import Enum


class MemoStatus(Enum):
    """メモの完了状態を列挙する値オブジェクト.

    Attributes:
        INCOMPLETE: 未完了状態
        COMPLETED: 完了状態
    """

    INCOMPLETE = "未完了"
    COMPLETED = "完了"

    def __str__(self) -> str:
        """状態の文字列値を返す.

        Returns:
            str: 状態を表す文字列
        """
        return self.value
