"""メモのタイトルの値オブジェクトを定義する."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoTitle:
    """メモのタイトルを表現する値オブジェクト.

    Attributes:
        value: タイトル文字列（1〜50文字）
    """

    value: str

    def __post_init__(self):
        """タイトル文字列のバリデーションを実行する.

        Raises:
            ValueError: タイトルが空, または50文字を超える場合
        """
        if not self.value:
            raise ValueError("Title is required")
        if len(self.value) > 50:
            raise ValueError("Title must be 50 characters or less")

    def __str__(self) -> str:
        """タイトル文字列を返す.

        Returns:
            str: ラップされたタイトル文字列
        """
        return self.value
