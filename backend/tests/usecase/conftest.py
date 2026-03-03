"""ユースケース層のテスト用共通フィクスチャ."""

from unittest.mock import AsyncMock

import pytest

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoDescription, MemoPriority, MemoTitle
from app.usecase import (
    CompleteMemoUseCase,
    CreateMemoUseCase,
    DeleteMemoUseCase,
    FindMemoByIdUseCase,
    FindMemosUseCase,
    UpdateMemoUseCase,
    new_complete_memo_usecase,
    new_create_memo_usecase,
    new_delete_memo_usecase,
    new_find_memo_by_id_usecase,
    new_find_memos_usecase,
    new_update_memo_usecase,
)


@pytest.fixture
def mock_memo_repository() -> MemoRepository:
    """モックメモリポジトリを提供する.

    各テストで必要に応じてモックの振る舞いをカスタマイズできる.

    Returns:
        MemoRepository: モックされたメモリポジトリ
    """
    return AsyncMock(spec=MemoRepository)


@pytest.fixture
def sample_memo() -> Memo:
    """テスト用のサンプルメモを提供する.

    Returns:
        Memo: デフォルト値で作成されたメモエンティティ
    """
    return Memo.create(
        title=MemoTitle("テストメモ"),
        description=MemoDescription("テスト用の説明"),
        priority=MemoPriority.MEDIUM,
    )


@pytest.fixture
def create_memo_usecase(mock_memo_repository: MemoRepository) -> CreateMemoUseCase:
    """CreateMemoUseCaseのインスタンスを提供する.

    Args:
        mock_memo_repository: モックされたメモリポジトリ

    Returns:
        CreateMemoUseCase: メモ作成ユースケース
    """
    return new_create_memo_usecase(mock_memo_repository)


@pytest.fixture
def update_memo_usecase(mock_memo_repository: MemoRepository) -> UpdateMemoUseCase:
    """UpdateMemoUseCaseのインスタンスを提供する.

    Args:
        mock_memo_repository: モックされたメモリポジトリ

    Returns:
        UpdateMemoUseCase: メモ更新ユースケース
    """
    return new_update_memo_usecase(mock_memo_repository)


@pytest.fixture
def complete_memo_usecase(mock_memo_repository: MemoRepository) -> CompleteMemoUseCase:
    """CompleteMemoUseCaseのインスタンスを提供する.

    Args:
        mock_memo_repository: モックされたメモリポジトリ

    Returns:
        CompleteMemoUseCase: メモ完了ユースケース
    """
    return new_complete_memo_usecase(mock_memo_repository)


@pytest.fixture
def find_memos_usecase(mock_memo_repository: MemoRepository) -> FindMemosUseCase:
    """FindMemosUseCaseのインスタンスを提供する.

    Args:
        mock_memo_repository: モックされたメモリポジトリ

    Returns:
        FindMemosUseCase: メモ一覧取得ユースケース
    """
    return new_find_memos_usecase(mock_memo_repository)


@pytest.fixture
def find_memo_by_id_usecase(
    mock_memo_repository: MemoRepository,
) -> FindMemoByIdUseCase:
    """FindMemoByIdUseCaseのインスタンスを提供する.

    Args:
        mock_memo_repository: モックされたメモリポジトリ

    Returns:
        FindMemoByIdUseCase: メモ個別取得ユースケース
    """
    return new_find_memo_by_id_usecase(mock_memo_repository)


@pytest.fixture
def delete_memo_usecase(mock_memo_repository: MemoRepository) -> DeleteMemoUseCase:
    """DeleteMemoUseCaseのインスタンスを提供する.

    Args:
        mock_memo_repository: モックされたメモリポジトリ

    Returns:
        DeleteMemoUseCase: メモ削除ユースケース
    """
    return new_delete_memo_usecase(mock_memo_repository)
