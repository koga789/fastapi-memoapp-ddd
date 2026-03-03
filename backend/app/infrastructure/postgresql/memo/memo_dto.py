"""メモエンティティとPostgreSQL永続化モデル間のマッピング."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities import Memo
from app.domain.value_objects import (
    MemoDescription,
    MemoDueDate,
    MemoId,
    MemoPriority,
    MemoStatus,
    MemoTitle,
)
from app.infrastructure.postgresql.db import Base


class MemoDTO(Base):
    """メモのPostgreSQL永続化モデルを表現する."""

    __tablename__ = "memos"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    def to_entity(self) -> Memo:
        """DTOをドメインエンティティに変換する.

        永続化層からの復元時は、値オブジェクトの reconstruct() メソッドを使用して
        バリデーションをスキップする。これは、保存時に既に検証済みのデータを
        再度検証する必要がないためである。

        Returns:
            Memo: 永続化された値から再構築されたドメインエンティティ
        """
        due_date = None
        if self.due_date:
            due_date = MemoDueDate.reconstruct(self.due_date.replace(tzinfo=UTC))

        created_at = self.created_at.replace(tzinfo=UTC)
        updated_at = self.updated_at.replace(tzinfo=UTC)

        return Memo(
            MemoId(self.id),
            MemoTitle(self.title),
            MemoDescription(self.description) if self.description else None,
            MemoPriority(self.priority),
            due_date,
            MemoStatus(self.status),
            created_at,
            updated_at,
        )

    @staticmethod
    def from_entity(memo: Memo) -> "MemoDTO":
        """ドメインエンティティからDTOを作成する.

        Args:
            memo: 変換するドメインエンティティ

        Returns:
            MemoDTO: 永続化のために準備されたDTO
        """
        return MemoDTO(
            id=memo.id.value,
            title=memo.title.value,
            description=memo.description.value if memo.description else None,
            priority=memo.priority.value,
            due_date=memo.due_date.value if memo.due_date else None,
            status=memo.status.value,
            created_at=memo.created_at,
            updated_at=memo.updated_at,
        )
