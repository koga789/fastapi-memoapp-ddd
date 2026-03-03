"""メモAPIエンドポイントのテスト."""

import uuid

import pytest
from app.infrastructure.di.injection import (
    get_complete_memo_usecase,
    get_create_memo_usecase,
    get_delete_memo_usecase,
    get_find_memo_by_id_usecase,
    get_find_memos_usecase,
    get_update_memo_usecase,
)
from httpx import AsyncClient

# ================================================================
# POST /memos/
# ================================================================


@pytest.mark.anyio
async def test_create_memo(integration_client: AsyncClient):
    """メモを作成できる."""
    # Arrange
    memo_data = {
        "title": "テストメモ",
        "description": "テスト用の説明",
        "priority": "高",
    }

    # Act
    response = await integration_client.post("/api/v1/memos/", json=memo_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "テストメモ"
    assert data["description"] == "テスト用の説明"
    assert data["priority"] == "高"
    assert data["status"] == "未完了"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_memo_with_minimum_fields(integration_client: AsyncClient):
    """最小限のフィールドでメモを作成できる."""
    # Arrange
    memo_data = {
        "title": "シンプルなメモ",
    }

    # Act
    response = await integration_client.post("/api/v1/memos/", json=memo_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "シンプルなメモ"
    assert data["description"] is None
    assert data["priority"] == "中"  # デフォルト値
    assert data["due_date"] is None


@pytest.mark.anyio
async def test_create_memo_with_invalid_title_raises_error(
    integration_client: AsyncClient,
):
    """無効なタイトルでメモ作成するとエラーが発生する."""
    # Arrange
    memo_data = {
        "title": "",  # 空のタイトル
    }

    # Act
    response = await integration_client.post("/api/v1/memos/", json=memo_data)

    # Assert
    # 空文字列はPydanticバリデーションで検出され422を返す
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_memo_value_error(integration_client: AsyncClient):
    """無効な優先度でメモ作成すると400エラーが発生する."""
    # Arrange
    memo_data = {
        "title": "テスト",
        "priority": "超高",
    }

    # Act
    response = await integration_client.post("/api/v1/memos/", json=memo_data)

    # Assert
    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_memo_internal_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースで予期しない例外が発生すると500を返す."""
    # Arrange
    failing_usecase(get_create_memo_usecase, RuntimeError("unexpected"))

    # Act
    response = await unit_client.post("/api/v1/memos/", json={"title": "テスト"})

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "メモの作成に失敗しました"


# ================================================================
# GET /memos/
# ================================================================


@pytest.mark.anyio
async def test_get_memos(integration_client: AsyncClient):
    """メモ一覧を取得できる."""
    # Arrange - API経由でメモを作成
    await integration_client.post("/api/v1/memos/", json={"title": "メモ1"})
    await integration_client.post("/api/v1/memos/", json={"title": "メモ2"})

    # Act
    response = await integration_client.get("/api/v1/memos/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    titles = {memo["title"] for memo in data}
    assert "メモ1" in titles
    assert "メモ2" in titles


@pytest.mark.anyio
async def test_get_memos_internal_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースで予期しない例外が発生すると500を返す."""
    # Arrange
    failing_usecase(get_find_memos_usecase, RuntimeError("unexpected"))

    # Act
    response = await unit_client.get("/api/v1/memos/")

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "メモの取得に失敗しました"


# ================================================================
# GET /memos/{id}
# ================================================================


@pytest.mark.anyio
async def test_get_memo_by_id(integration_client: AsyncClient):
    """IDでメモを取得できる."""
    # Arrange - API経由でメモを作成
    create_response = await integration_client.post(
        "/api/v1/memos/",
        json={
            "title": "テストメモ",
            "description": "詳細説明",
        },
    )
    memo_id = create_response.json()["id"]

    # Act
    response = await integration_client.get(f"/api/v1/memos/{memo_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == memo_id
    assert data["title"] == "テストメモ"
    assert data["description"] == "詳細説明"


@pytest.mark.anyio
async def test_get_memo_by_id_not_found(integration_client: AsyncClient):
    """存在しないIDでメモを取得すると404エラーが発生する."""
    # Arrange
    non_existent_id = uuid.uuid4()

    # Act
    response = await integration_client.get(f"/api/v1/memos/{non_existent_id}")

    # Assert
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_memo_internal_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースで予期しない例外が発生すると500を返す."""
    # Arrange
    target_id = uuid.uuid4()
    failing_usecase(get_find_memo_by_id_usecase, RuntimeError("unexpected"))

    # Act
    response = await unit_client.get(f"/api/v1/memos/{target_id}")

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "メモの取得に失敗しました"


# ================================================================
# PUT /memos/{id}
# ================================================================


@pytest.mark.anyio
async def test_update_memo(integration_client: AsyncClient):
    """メモを更新できる."""
    # Arrange - API経由でメモを作成
    create_response = await integration_client.post(
        "/api/v1/memos/",
        json={
            "title": "元のタイトル",
            "description": "元の説明",
        },
    )
    memo_id = create_response.json()["id"]
    update_data = {
        "title": "新しいタイトル",
        "description": "新しい説明",
    }

    # Act
    response = await integration_client.put(
        f"/api/v1/memos/{memo_id}", json=update_data
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "新しいタイトル"
    assert data["description"] == "新しい説明"


@pytest.mark.anyio
async def test_update_memo_not_found(integration_client: AsyncClient):
    """存在しないメモを更新すると404エラーが発生する."""
    # Arrange
    non_existent_id = uuid.uuid4()
    update_data = {
        "title": "新しいタイトル",
    }

    # Act
    response = await integration_client.put(
        f"/api/v1/memos/{non_existent_id}", json=update_data
    )

    # Assert
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_memo_value_error(integration_client: AsyncClient):
    """無効な優先度でメモ更新すると400エラーが発生する."""
    # Arrange
    target_id = uuid.uuid4()
    update_data = {
        "priority": "超高",
    }

    # Act
    response = await integration_client.put(
        f"/api/v1/memos/{target_id}", json=update_data
    )

    # Assert
    assert response.status_code == 400


@pytest.mark.anyio
async def test_update_memo_internal_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースで予期しない例外が発生すると500を返す."""
    # Arrange
    target_id = uuid.uuid4()
    failing_usecase(get_update_memo_usecase, RuntimeError("unexpected"))

    # Act
    response = await unit_client.put(
        f"/api/v1/memos/{target_id}", json={"title": "テスト"}
    )

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "メモの更新に失敗しました"


# ================================================================
# PATCH /memos/{id}/complete
# ================================================================


@pytest.mark.anyio
async def test_complete_memo(integration_client: AsyncClient):
    """メモを完了状態にできる."""
    # Arrange - API経由でメモを作成
    create_response = await integration_client.post(
        "/api/v1/memos/",
        json={"title": "完了対象のメモ"},
    )
    memo_id = create_response.json()["id"]

    # Act
    response = await integration_client.patch(f"/api/v1/memos/{memo_id}/complete")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "完了"


@pytest.mark.anyio
async def test_complete_memo_not_found(integration_client: AsyncClient):
    """存在しないメモを完了しようとすると404エラーが発生する."""
    # Arrange
    non_existent_id = uuid.uuid4()

    # Act
    response = await integration_client.patch(
        f"/api/v1/memos/{non_existent_id}/complete"
    )

    # Assert
    assert response.status_code == 404


@pytest.mark.anyio
async def test_complete_memo_value_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースがValueErrorを送出すると400を返す."""
    # Arrange
    target_id = uuid.uuid4()
    failing_usecase(get_complete_memo_usecase, ValueError("既に完了済みです"))

    # Act
    response = await unit_client.patch(f"/api/v1/memos/{target_id}/complete")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "既に完了済みです"


@pytest.mark.anyio
async def test_complete_memo_internal_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースで予期しない例外が発生すると500を返す."""
    # Arrange
    target_id = uuid.uuid4()
    failing_usecase(get_complete_memo_usecase, RuntimeError("unexpected"))

    # Act
    response = await unit_client.patch(f"/api/v1/memos/{target_id}/complete")

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "メモの完了に失敗しました"


# ================================================================
# DELETE /memos/{id}
# ================================================================


@pytest.mark.anyio
async def test_delete_memo(integration_client: AsyncClient):
    """メモを削除できる."""
    # Arrange - API経由でメモを作成
    create_response = await integration_client.post(
        "/api/v1/memos/",
        json={"title": "削除対象のメモ"},
    )
    memo_id = create_response.json()["id"]

    # Act
    response = await integration_client.delete(f"/api/v1/memos/{memo_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # 削除されたことを確認
    get_response = await integration_client.get(f"/api/v1/memos/{memo_id}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_memo_not_found(integration_client: AsyncClient):
    """存在しないメモを削除しようとすると404エラーが発生する."""
    # Arrange
    non_existent_id = uuid.uuid4()

    # Act
    response = await integration_client.delete(f"/api/v1/memos/{non_existent_id}")

    # Assert
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_memo_internal_error(unit_client: AsyncClient, failing_usecase):
    """ユースケースで予期しない例外が発生すると500を返す."""
    # Arrange
    target_id = uuid.uuid4()
    failing_usecase(get_delete_memo_usecase, RuntimeError("unexpected"))

    # Act
    response = await unit_client.delete(f"/api/v1/memos/{target_id}")

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "メモの削除に失敗しました"
