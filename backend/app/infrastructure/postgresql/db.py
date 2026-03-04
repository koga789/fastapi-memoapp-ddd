"""PostgreSQL用のデータベース設定とセッション管理."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# 非同期エンジンの作成
async_engine = create_async_engine(settings.sqlalchemy_database_uri)

# 非同期セッションの設定
async_session = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# ベースクラスの定義
Base = declarative_base()
