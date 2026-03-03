"""メモ作成のユースケース実装を提供する."""

from abc import ABC, abstractmethod

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoPriority,
    MemoTitle,
)


class CreateMemoUseCase(ABC):
    """メモ作成のアプリケーション境界を定義する."""

    @abstractmethod
    async def execute(
        self,
        title: MemoTitle,
        description: MemoDescription | None = None,
        priority: MemoPriority = MemoPriority.MEDIUM,
        due_date: MemoDueDate | None = None,
    ) -> Memo:
        """提供された値を使用してメモを作成する.

        Args:
            title: メモのタイトル
            description: メモの詳細（任意）
            priority: メモの優先度（デフォルト: MEDIUM）
            due_date: メモの期限日（任意）

        Returns:
            Memo: 新規作成されたメモエンティティ
        """


class CreateMemoUseCaseImpl(CreateMemoUseCase):
    """リポジトリに支えられた具体的なメモ作成ユースケース."""

    def __init__(self, memo_repository: MemoRepository):
        """リポジトリ依存関係を保存する.

        Args:
            memo_repository: メモを永続化するリポジトリ
        """
        self.memo_repository = memo_repository

    async def execute(
        self,
        title: MemoTitle,
        description: MemoDescription | None = None,
        priority: MemoPriority = MemoPriority.MEDIUM,
        due_date: MemoDueDate | None = None,
    ) -> Memo:
        """メモを作成, 永続化し, 返却する.

        Args:
            title: メモのタイトル
            description: メモの詳細（任意）
            priority: メモの優先度（デフォルト: MEDIUM）
            due_date: メモの期限日（任意）

        Returns:
            Memo: 新規作成されたメモエンティティ
        """
        memo = Memo.create(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        await self.memo_repository.save(memo)
        return memo


def new_create_memo_usecase(memo_repository: MemoRepository) -> CreateMemoUseCase:
    """メモ作成ユースケースをインスタンス化する.

    Args:
        memo_repository: メモを永続化するリポジトリ

    Returns:
        CreateMemoUseCase: 設定済みのユースケース実装
    """
    return CreateMemoUseCaseImpl(memo_repository)
