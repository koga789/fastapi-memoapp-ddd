"""メモエンティティのリポジトリ抽象化を定義する."""

from abc import ABC, abstractmethod

from app.domain.entities import Memo
from app.domain.value_objects import MemoId


class MemoRepository(ABC):
    """メモの永続化操作の抽象化を提供する."""

    @abstractmethod
    async def save(self, memo: Memo) -> None:
        """提供されたメモエンティティを永続化する.

        Args:
            memo: 保存または更新するMemoインスタンス
        """

    @abstractmethod
    async def find_by_id(self, memo_id: MemoId) -> Memo | None:
        """識別子でメモを取得する.

        Args:
            memo_id: 取得するメモの識別子

        Returns:
            Memo | None: 見つかった場合はMemo, 見つからない場合はNone
        """

    @abstractmethod
    async def find_all(self) -> list[Memo]:
        """リポジトリに保存されているメモのコレクションを返す.

        Returns:
            list[Memo]: 永続化されているすべてのメモ
        """

    @abstractmethod
    async def delete(self, memo_id: MemoId) -> None:
        """提供されたIDで識別されるメモを削除する.

        Args:
            memo_id: 削除するメモの識別子
        """
