"""メモ個別取得のユースケース実装を提供する."""

from abc import ABC, abstractmethod

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId


class FindMemoByIdUseCase(ABC):
    """メモ個別取得のアプリケーション境界を定義する."""

    @abstractmethod
    async def execute(self, memo_id: MemoId) -> Memo:
        """提供された識別子に一致するメモを返す.

        Args:
            memo_id: 取得するメモの識別子

        Returns:
            Memo: 指定された識別子と一致するメモエンティティ
        """


class FindMemoByIdUseCaseImpl(FindMemoByIdUseCase):
    """リポジトリに支えられた具体的なメモ個別取得ユースケース."""

    def __init__(self, memo_repository: MemoRepository):
        """リポジトリ依存関係を保存する.

        Args:
            memo_repository: メモを取得するリポジトリ
        """
        self.memo_repository = memo_repository

    async def execute(self, memo_id: MemoId) -> Memo:
        """識別子でメモを取得するか, 存在しない場合は例外を投げる.

        Args:
            memo_id: 取得するメモの識別子

        Raises:
            MemoNotFoundError: メモが見つからない場合

        Returns:
            Memo: 一致するメモエンティティ
        """
        memo = await self.memo_repository.find_by_id(memo_id)
        if memo is None:
            raise MemoNotFoundError
        return memo


def new_find_memo_by_id_usecase(
    memo_repository: MemoRepository,
) -> FindMemoByIdUseCase:
    """メモ個別取得ユースケースをインスタンス化する.

    Args:
        memo_repository: メモを取得するリポジトリ

    Returns:
        FindMemoByIdUseCase: 設定済みのユースケース実装
    """
    return FindMemoByIdUseCaseImpl(memo_repository)
