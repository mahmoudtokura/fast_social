import pytest
from httpx import AsyncClient


async def register_user(email: str, password: str, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/register",
        json={
            "email": email,
            "password": password,
        },
    )

    return response


@pytest.fixture()
async def create_new_user(async_client: AsyncClient) -> dict:
    return await register_user("testuser@testuser.com", "testing1234", async_client)


@pytest.mark.anyio
async def test_create_new_user(async_client: AsyncClient):
    user = {"email": "testuser@testuser.com", "password": "testing1234"}
    response = await register_user(user["email"], user["password"], async_client)

    assert response.status_code == 201
    assert "User created" in response.json()["details"]


@pytest.mark.anyio
async def test_create_user_already_exits(
    async_client: AsyncClient, registered_user: dict
):
    response = await register_user(
        registered_user["email"], registered_user["password"], async_client
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exits(async_client: AsyncClient):
    response = await async_client.post(
        "/token",
        json={
            "email": "nonuser@test.com",
            "password": "password",
        },
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user_exits(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    assert "bearer" in response.json()["token_type"]
