"""メモ更新のユースケース実装を提供する."""

from abc import ABC, abstractmethod

from app.domain.entities import Memo
from app.domain.exceptions import MemoNotFoundError
from app.domain.repositories import MemoRepository
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoTitle,
)


class UpdateMemoUseCase(ABC):
    """メモ更新のアプリケーション境界を定義する."""

    @abstractmethod
    async def execute(
        self,
        memo_id: MemoId,
        title: MemoTitle | None = None,
        description: MemoDescription | None = None,
        priority: MemoPriority | None = None,
        due_date: MemoDueDate | None = None,
    ) -> Memo:
        """提供された値を使用してメモを更新する.

        Args:
            memo_id: 更新するメモの識別子
            title: 新しいタイトル（任意）
            description: 新しい詳細（任意）
            priority: 新しい優先度（任意）
            due_date: 新しい期限日（任意）

        Returns:
            Memo: 更新されたメモエンティティ
        """


class UpdateMemoUseCaseImpl(UpdateMemoUseCase):
    """リポジトリに支えられた具体的なメモ更新ユースケース."""

    def __init__(self, memo_repository: MemoRepository):
        """リポジトリ依存関係を保存する.

        Args:
            memo_repository: メモを永続化するリポジトリ
        """
        self.memo_repository = memo_repository

    async def execute(
        self,
        memo_id: MemoId,
        title: MemoTitle | None = None,
        description: MemoDescription | None = None,
        priority: MemoPriority | None = None,
        due_date: MemoDueDate | None = None,
    ) -> Memo:
        """メモを更新し, 変更を永続化する.

        Args:
            memo_id: 更新するメモの識別子
            title: 新しいタイトル（任意）
            description: 新しい詳細（任意）
            priority: 新しい優先度（任意）
            due_date: 新しい期限日（任意）

        Raises:
            MemoNotFoundError: 指定された識別子のメモが見つからない場合

        Returns:
            Memo: 更新されたメモエンティティ
        """
        memo = await self.memo_repository.find_by_id(memo_id)

        if memo is None:
            raise MemoNotFoundError

        if title is not None:
            memo.update_title(title)
        if description is not None:
            memo.update_description(description)
        if priority is not None:
            memo.update_priority(priority)
        if due_date is not None:
            memo.update_due_date(due_date)

        await self.memo_repository.save(memo)
        return memo


def new_update_memo_usecase(memo_repository: MemoRepository) -> UpdateMemoUseCase:
    """メモ更新ユースケースをインスタンス化する.

    Args:
        memo_repository: メモを永続化するリポジトリ

    Returns:
        UpdateMemoUseCase: 設定済みのユースケース実装
    """
    return UpdateMemoUseCaseImpl(memo_repository)
