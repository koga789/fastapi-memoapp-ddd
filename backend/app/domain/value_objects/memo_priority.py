"""メモの優先度の列挙型を定義する."""

from enum import Enum


class MemoPriority(Enum):
    """メモの優先度レベルを列挙する値オブジェクト.

    Attributes:
        LOW: 低
        MEDIUM: 中
        HIGH: 高
    """

    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"

    def __str__(self) -> str:
        """優先度の文字列値を返す.

        Returns:
            str: 優先度を表す文字列
        """
        return self.value
