"""メモ削除のユースケース実装を提供する."""

from abc import ABC, abstractmethod

from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId


class DeleteMemoUseCase(ABC):
    """メモ削除のアプリケーション境界を定義する."""

    @abstractmethod
    async def execute(self, memo_id: MemoId) -> None:
        """提供されたIDで識別されるメモを削除する.

        Args:
            memo_id: 削除するメモの識別子
        """


class DeleteMemoUseCaseImpl(DeleteMemoUseCase):
    """リポジトリに支えられた具体的なメモ削除ユースケース."""

    def __init__(self, memo_repository: MemoRepository):
        """リポジトリ依存関係を保存する.

        Args:
            memo_repository: メモの永続化を担当するリポジトリ
        """
        self.memo_repository = memo_repository

    async def execute(self, memo_id: MemoId) -> None:
        """メモの存在を確認した後, 削除する.

        Args:
            memo_id: 削除するメモの識別子

        Raises:
            MemoNotFoundError: 指定された識別子のメモが見つからない場合
        """
        memo = await self.memo_repository.find_by_id(memo_id)

        if memo is None:
            raise MemoNotFoundError

        await self.memo_repository.delete(memo_id)


def new_delete_memo_usecase(memo_repository: MemoRepository) -> DeleteMemoUseCase:
    """メモ削除ユースケースをインスタンス化する.

    Args:
        memo_repository: メモの永続化を担当するリポジトリ

    Returns:
        DeleteMemoUseCase: 設定済みのユースケース実装
    """
    return DeleteMemoUseCaseImpl(memo_repository)
