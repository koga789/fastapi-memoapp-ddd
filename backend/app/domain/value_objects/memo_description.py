"""メモの説明の値オブジェクトを定義する."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoDescription:
    """メモの詳細説明を表現する値オブジェクト.

    Attributes:
        value: 詳細（0〜255文字）
    """

    value: str

    def __post_init__(self):
        """詳細文字列の長さをバリデーションする.

        Raises:
            ValueError: 詳細が255文字を超える場合
        """
        if len(self.value) > 255:
            raise ValueError("Description must be 255 characters or less")

    def __str__(self) -> str:
        """詳細文字列を返す.

        Returns:
            str: ラップされた詳細文字列
        """
        return self.value
