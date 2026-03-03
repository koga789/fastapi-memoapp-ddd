"""メモ一覧取得のユースケース実装を提供する."""

from abc import ABC, abstractmethod

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository


class FindMemosUseCase(ABC):
    """メモ一覧取得のアプリケーション境界を定義する."""

    @abstractmethod
    async def execute(self) -> list[Memo]:
        """システムで管理されているメモのコレクションを返す.

        Returns:
            list[Memo]: 永続化されているすべてのメモエンティティ
        """


class FindMemosUseCaseImpl(FindMemosUseCase):
    """リポジトリに支えられた具体的なメモ一覧取得ユースケース."""

    def __init__(self, memo_repository: MemoRepository):
        """リポジトリ依存関係を保存する.

        Args:
            memo_repository: メモを取得するリポジトリ
        """
        self.memo_repository = memo_repository

    async def execute(self) -> list[Memo]:
        """リポジトリ実装に従って並べられたすべてのメモを返す."""
        return await self.memo_repository.find_all()


def new_find_memos_usecase(memo_repository: MemoRepository) -> FindMemosUseCase:
    """メモ一覧取得ユースケースをインスタンス化する.

    Args:
        memo_repository: メモを取得するリポジトリ

    Returns:
        FindMemosUseCase: 設定済みのユースケース実装
    """
    return FindMemosUseCaseImpl(memo_repository)
