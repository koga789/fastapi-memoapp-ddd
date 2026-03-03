"""ユースケース層が必要とするインターフェース定義."""

from app.usecase.interfaces.logger import Logger, LoggerFactory

__all__ = ["Logger", "LoggerFactory"]
