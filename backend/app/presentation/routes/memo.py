"""メモ関連のHTTPリクエストを処理."""

from uuid import UUID

from app.domain.exceptions import MemoNotFoundError
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoTitle,
)
from app.infrastructure.di.injection import (
    get_complete_memo_usecase,
    get_create_memo_usecase,
    get_delete_memo_usecase,
    get_find_memo_by_id_usecase,
    get_find_memos_usecase,
    get_update_memo_usecase,
)
from app.presentation.schemas.memo import (
    MemoCreateSchema,
    MemoResponseSchema,
    MemoUpdateSchema,
    MessageResponseSchema,
)
from app.usecase import (
    CompleteMemoUseCase,
    CreateMemoUseCase,
    DeleteMemoUseCase,
    FindMemoByIdUseCase,
    FindMemosUseCase,
    UpdateMemoUseCase,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/memos", tags=["memos"])


@router.post(
    "/",
    response_model=MemoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="メモを新規作成",
    description="新しいメモを作成します. (タイトルは必須)",
)
async def create_memo(
    memo: MemoCreateSchema,
    usecase: CreateMemoUseCase = Depends(get_create_memo_usecase),
):
    """新しいメモを作成する.

    Args:
        memo: メモの作成リクエスト
        usecase: メモ作成を担当するユースケース

    Returns:
        MemoResponseSchema: 作成されたメモ

    Raises:
        HTTPException: メモの作成に失敗した場合
    """
    try:
        created_memo = await usecase.execute(
            title=MemoTitle(memo.title),
            description=MemoDescription(memo.description) if memo.description else None,
            priority=MemoPriority(memo.priority),
            due_date=MemoDueDate.create(memo.due_date) if memo.due_date else None,
        )
        return MemoResponseSchema.from_entity(created_memo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メモの作成に失敗しました",
        ) from e


@router.get(
    "/",
    response_model=list[MemoResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="メモ一覧を取得",
    description="すべてのメモを取得します.",
)
async def get_memos(
    usecase: FindMemosUseCase = Depends(get_find_memos_usecase),
):
    """すべてのメモを取得する.

    Args:
        usecase: メモ一覧取得を担当するユースケース

    Returns:
        list[MemoResponseSchema]: メモのリスト

    Raises:
        HTTPException: メモの取得に失敗した場合
    """
    try:
        memos = await usecase.execute()
        return [MemoResponseSchema.from_entity(memo) for memo in memos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メモの取得に失敗しました",
        ) from e


@router.get(
    "/{memo_id}",
    response_model=MemoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="メモを個別取得",
    description="指定されたIDのメモを取得します.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "メモが見つかりません",
        },
    },
)
async def get_memo(
    memo_id: UUID,
    usecase: FindMemoByIdUseCase = Depends(get_find_memo_by_id_usecase),
):
    """指定されたIDのメモを取得する.

    Args:
        memo_id: 取得するメモのID
        usecase: メモ個別取得を担当するユースケース

    Returns:
        MemoResponseSchema: メモ

    Raises:
        HTTPException: メモが見つからない場合、または取得に失敗した場合
    """
    _id = MemoId(memo_id)
    try:
        memo = await usecase.execute(_id)
        return MemoResponseSchema.from_entity(memo)
    except MemoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メモの取得に失敗しました",
        ) from e


@router.put(
    "/{memo_id}",
    response_model=MemoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="メモを更新",
    description="指定されたIDのメモを更新します.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "メモが見つかりません",
        },
    },
)
async def update_memo(
    memo_id: UUID,
    memo: MemoUpdateSchema,
    usecase: UpdateMemoUseCase = Depends(get_update_memo_usecase),
):
    """指定されたIDのメモを更新する.

    Args:
        memo_id: 更新するメモのID
        memo: メモの更新リクエスト
        usecase: メモ更新を担当するユースケース

    Returns:
        MemoResponseSchema: 更新されたメモ

    Raises:
        HTTPException: メモが見つからない場合、または更新に失敗した場合
    """
    _id = MemoId(memo_id)

    try:
        title = MemoTitle(memo.title) if memo.title is not None else None
        description = (
            MemoDescription(memo.description) if memo.description is not None else None
        )
        priority = MemoPriority(memo.priority) if memo.priority is not None else None
        due_date = (
            MemoDueDate.create(memo.due_date) if memo.due_date is not None else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    try:
        updated_memo = await usecase.execute(
            memo_id=_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        return MemoResponseSchema.from_entity(updated_memo)
    except MemoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メモの更新に失敗しました",
        ) from e


@router.patch(
    "/{memo_id}/complete",
    response_model=MemoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="メモを完了",
    description="指定されたIDのメモを完了状態にします.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "メモが見つかりません",
        },
    },
)
async def complete_memo(
    memo_id: UUID,
    usecase: CompleteMemoUseCase = Depends(get_complete_memo_usecase),
):
    """指定されたIDのメモを完了状態にする.

    Args:
        memo_id: 完了するメモのID
        usecase: メモ完了を担当するユースケース

    Returns:
        MemoResponseSchema: 完了したメモ

    Raises:
        HTTPException: メモが見つからない場合、または完了に失敗した場合
    """
    _id = MemoId(memo_id)
    try:
        completed_memo = await usecase.execute(_id)
        return MemoResponseSchema.from_entity(completed_memo)
    except MemoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メモの完了に失敗しました",
        ) from e


@router.delete(
    "/{memo_id}",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="メモを削除",
    description="指定されたIDのメモを削除します.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "メモが見つかりません",
        },
    },
)
async def delete_memo(
    memo_id: UUID,
    usecase: DeleteMemoUseCase = Depends(get_delete_memo_usecase),
):
    """指定されたIDのメモを削除する.

    Args:
        memo_id: 削除するメモのID
        usecase: メモ削除を担当するユースケース

    Returns:
        MessageResponseSchema: 削除成功メッセージ

    Raises:
        HTTPException: メモが見つからない場合、または削除に失敗した場合
    """
    _id = MemoId(memo_id)
    try:
        await usecase.execute(_id)
        return MessageResponseSchema(message="メモが正常に削除されました")
    except MemoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メモの削除に失敗しました",
        ) from e
