"""tests_pre_start モジュールのユニットテスト."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import text

from app.tests_pre_start import init


class TestInit:
    """init 関数のテスト."""

    @pytest.mark.anyio
    @patch("app.tests_pre_start.async_session")
    async def test_init_successful_connection(
        self,
        mock_async_session: MagicMock,
    ) -> None:
        """データベース接続の疎通確認が成功することを検証."""
        # Arrange
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_async_session.return_value.__aexit__ = AsyncMock(return_value=None)

        # Act
        await init()

        # Assert
        # text() オブジェクト同士は == で等価比較できないため、
        # assert_awaited_once_with(text("SELECT 1")) は使用できない。
        # await_args から引数を取り出し、str() で SQL 文字列に変換して比較する。
        # Ref: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.await_args
        mock_session.execute.assert_awaited_once()
        actual_arg = mock_session.execute.await_args[0][0]
        assert str(actual_arg) == str(text("SELECT 1"))
