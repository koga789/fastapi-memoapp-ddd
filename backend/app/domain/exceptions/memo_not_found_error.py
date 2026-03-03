"""欠落しているメモエンティティの例外を定義する."""


class MemoNotFoundError(Exception):
    """要求されたメモエンティティが見つからない場合に発生する."""

    message = "The Memo you specified does not exist."

    def __str__(self):
        """デフォルトの人間が読めるエラーメッセージを返す.

        Returns:
            str: エラーメッセージ
        """
        return MemoNotFoundError.message
