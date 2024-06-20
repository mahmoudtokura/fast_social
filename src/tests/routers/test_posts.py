import pytest
from httpx import AsyncClient


async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/post",
        json={"body": body},
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient) -> dict:
    return await create_post("Test Post", async_client)

@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict) -> dict:
    response = await async_client.post(
        "/comment",
        json={"body": "Test Comment", "post_id": created_post["id"]},
    )
    return response.json()


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test Post"
    response = await async_client.post(
        "/post",
        json={"body": body},
    )
    assert response.status_code == 201
    assert response.json().items() >= {"id": 1, "body": "Test Post"}.items()


@pytest.mark.anyio
async def test_create_post_without_body(async_client: AsyncClient):
    response = await async_client.post(
        "/post",
        json={},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    post_id = created_post["id"]
    body = "A comment on the first post"
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": post_id},
    )
    assert response.status_code == 201
    assert (
        response.json().items()
        >= {
            "id": 1,
            "body": body,
            "post_id": created_post["id"],
        }.items()
    )


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post["id"]}/comment")
    assert response.status_code == 200
    assert response.json() == [created_comment]

@pytest.mark.anyio
async def test_get_empty_comments_on_post(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/post/{created_post["id"]}/comment")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_post_with_comments(async_client: AsyncClient, created_post: dict, created_comment: dict):
    response = await async_client.get(f"/post/{created_post["id"]}")
    assert response.status_code == 200
    assert response.json() == {
        "post": created_post,
        "comments": [created_comment],
    }


@pytest.mark.anyio
async def test_get_comment_on_post_not_found(async_client: AsyncClient, created_post: dict, created_comment: dict):
    response = await async_client.get("/post/4/comment")
    assert response.status_code == 404
