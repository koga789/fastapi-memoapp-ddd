"""ドメインリポジトリインターフェースをエクスポートする."""

from app.domain.repositories.memo_repository import MemoRepository

__all__ = ["MemoRepository"]
