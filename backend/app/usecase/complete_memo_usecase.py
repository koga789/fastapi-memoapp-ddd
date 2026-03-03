"""メモ完了のユースケース実装を提供する."""

from abc import ABC, abstractmethod

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId


class CompleteMemoUseCase(ABC):
    """メモ完了のアプリケーション境界を定義する."""

    @abstractmethod
    async def execute(self, memo_id: MemoId) -> Memo:
        """提供されたIDで識別されるメモを完了する.

        Args:
            memo_id: 完了するメモの識別子

        Returns:
            Memo: 完了状態に更新されたメモエンティティ
        """


class CompleteMemoUseCaseImpl(CompleteMemoUseCase):
    """リポジトリに支えられた具体的なメモ完了ユースケース."""

    def __init__(self, memo_repository: MemoRepository):
        """リポジトリ依存関係を保存する.

        Args:
            memo_repository: メモを永続化するリポジトリ
        """
        self.memo_repository = memo_repository

    async def execute(self, memo_id: MemoId) -> Memo:
        """メモの状態を検証した後, 完了する.

        Args:
            memo_id: 完了するメモの識別子

        Raises:
            MemoNotFoundError: メモが見つからない場合

        Returns:
            Memo: 完了状態に更新されたメモエンティティ
        """
        memo = await self.memo_repository.find_by_id(memo_id)

        if memo is None:
            raise MemoNotFoundError

        memo.complete()
        await self.memo_repository.save(memo)
        return memo


def new_complete_memo_usecase(memo_repository: MemoRepository) -> CompleteMemoUseCase:
    """メモ完了ユースケースをインスタンス化する.

    Args:
        memo_repository: メモを永続化するリポジトリ

    Returns:
        CompleteMemoUseCase: 設定済みのユースケース実装
    """
    return CompleteMemoUseCaseImpl(memo_repository)
