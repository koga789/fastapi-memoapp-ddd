"""メモリソースのリクエスト/レスポンススキーマを定義する."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import Memo


class MemoCreateSchema(BaseModel):
    """メモ作成のペイロードを検証する.

    Attributes:
        title: メモのタイトル
        description: メモの詳細説明（任意）
        priority: メモの優先度（デフォルト: 中）
        due_date: メモの期限日（任意）
    """

    title: str = Field(
        min_length=1,
        max_length=50,
        description="メモのタイトル",
        examples=["会議の準備"],
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="メモの詳細説明",
        examples=["明日の会議で使用する資料を準備する"],
    )
    priority: str = Field(
        default="中",
        description="メモの優先度（低、中、高）",
        examples=["高"],
    )
    due_date: datetime | None = Field(
        default=None,
        description="メモの期限日",
        examples=["2026-01-20T10:00:00"],
    )


class MemoUpdateSchema(BaseModel):
    """メモ更新のペイロードを検証する.

    Attributes:
        title: メモのタイトル（任意）
        description: メモの詳細説明（任意）
        priority: メモの優先度（任意）
        due_date: メモの期限日（任意）
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="メモのタイトル",
        examples=["会議の準備"],
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="メモの詳細説明",
        examples=["明日の会議で使用する資料を準備する"],
    )
    priority: str | None = Field(
        default=None,
        description="メモの優先度（低、中、高）",
        examples=["高"],
    )
    due_date: datetime | None = Field(
        default=None,
        description="メモの期限日",
        examples=["2026-01-20T10:00:00"],
    )


class MemoResponseSchema(BaseModel):
    """クライアントに返されるメモのシリアライズされたビューを表現する.

    Attributes:
        id: メモの一意識別子
        title: メモのタイトル
        description: メモの詳細説明
        priority: メモの優先度
        due_date: メモの期限日（UNIXタイムスタンプ、ミリ秒）
        status: メモの完了状態
        created_at: メモの作成日時（UNIXタイムスタンプ、ミリ秒）
        updated_at: メモの最終更新日時（UNIXタイムスタンプ、ミリ秒）
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        description="メモの一意識別子",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    title: str = Field(
        description="メモのタイトル",
        examples=["会議の準備"],
    )
    description: str | None = Field(
        description="メモの詳細説明",
        examples=["明日の会議で使用する資料を準備する"],
    )
    priority: str = Field(
        description="メモの優先度",
        examples=["高"],
    )
    due_date: int | None = Field(
        description="メモの期限日（UNIXタイムスタンプ、ミリ秒）",
        examples=[1705311600000],
    )
    status: str = Field(
        description="メモの完了状態",
        examples=["未完了"],
    )
    created_at: int = Field(
        description="メモの作成日時（UNIXタイムスタンプ、ミリ秒）",
        examples=[1705225200000],
    )
    updated_at: int = Field(
        description="メモの最終更新日時（UNIXタイムスタンプ、ミリ秒）",
        examples=[1705225200000],
    )

    @staticmethod
    def from_entity(memo: Memo) -> "MemoResponseSchema":
        """ドメインエンティティから表示用インスタンスを構築する.

        Args:
            memo: 変換するドメインエンティティ

        Returns:
            MemoResponseSchema: シリアライズされたPydanticモデル
        """
        return MemoResponseSchema(
            id=str(memo.id.value),
            title=memo.title.value,
            description=memo.description.value if memo.description else None,
            priority=memo.priority.value,
            due_date=int(memo.due_date.value.timestamp() * 1000) if memo.due_date else None,
            status=memo.status.value,
            created_at=int(memo.created_at.timestamp() * 1000),
            updated_at=int(memo.updated_at.timestamp() * 1000),
        )


class MessageResponseSchema(BaseModel):
    """シンプルなメッセージレスポンスを表現する.

    Attributes:
        message: 処理結果のメッセージ
    """

    message: str = Field(
        description="処理結果のメッセージ",
        examples=["メモが正常に作成されました"],
    )
