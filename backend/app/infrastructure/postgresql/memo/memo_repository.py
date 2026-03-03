"""メモリポジトリのPostgreSQL実装."""

from sqlalchemy import delete, desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Memo
from app.domain.repositories import MemoRepository
from app.domain.value_objects import MemoId
from app.infrastructure.postgresql.memo import MemoDTO


class MemoRepositoryImpl(MemoRepository):
    """SQLAlchemyとPostgreSQLバックエンドを使用してメモを永続化する."""

    def __init__(self, session: AsyncSession):
        """SQLAlchemyセッション依存関係を保存する.

        Args:
            session: PostgreSQLエンジンにバインドされたアクティブなSQLAlchemyセッション
        """
        self.session = session

    async def find_by_id(self, memo_id: MemoId) -> Memo | None:
        """提供された識別子に一致するメモを返す.

        Args:
            memo_id: 取得するメモの識別子

        Returns:
            Memo | None: 見つかった場合はMemo, 見つからない場合はNone
        """
        try:
            result = await self.session.execute(select(MemoDTO).where(MemoDTO.id == memo_id.value))
            row = result.scalar_one()
        except NoResultFound:
            return None

        return row.to_entity()

    async def find_all(self) -> list[Memo]:
        """作成日時で並べられたメモを返す.

        Returns:
            list[Memo]: 作成日時の降順で並べられたすべてのメモ
        """
        result = await self.session.execute(select(MemoDTO).order_by(desc(MemoDTO.created_at)))
        rows = result.scalars().all()
        return [memo_dto.to_entity() for memo_dto in rows]

    async def save(self, memo: Memo) -> None:
        """新規または更新されたメモデータを永続化する.

        Args:
            memo: 作成または更新するMemoエンティティ
        """
        memo_dto = MemoDTO.from_entity(memo)
        try:
            result = await self.session.execute(select(MemoDTO).where(MemoDTO.id == memo.id.value))
            existing_memo = result.scalar_one()
        except NoResultFound:
            self.session.add(memo_dto)
        else:
            existing_memo.title = memo_dto.title
            existing_memo.description = memo_dto.description
            existing_memo.priority = memo_dto.priority
            existing_memo.due_date = memo_dto.due_date
            existing_memo.status = memo_dto.status
            existing_memo.updated_at = memo_dto.updated_at

        await self.session.flush()

    async def delete(self, memo_id: MemoId) -> None:
        """識別子でメモを削除する.

        Args:
            memo_id: 削除するメモの識別子
        """
        await self.session.execute(delete(MemoDTO).where(MemoDTO.id == memo_id.value))
        await self.session.flush()


def new_memo_repository(session: AsyncSession) -> MemoRepository:
    """メモリポジトリをインスタンス化する.

    Args:
        session: PostgreSQLエンジンにバインドされたアクティブなSQLAlchemyセッション

    Returns:
        MemoRepository: 設定済みのリポジトリ実装
    """
    return MemoRepositoryImpl(session)
