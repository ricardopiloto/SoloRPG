import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, register_user, verify_user


@pytest.mark.asyncio
async def test_login_after_verify(client: AsyncClient, clear_mock_codes, multi_user):
    await register_user(client)
    await verify_user(client)
    res = await client.post(
        "/api/auth/login",
        json={"email": "player@example.com", "password": "secret123"},
    )
    assert res.status_code == 200
    assert res.json()["access_token"]


@pytest.mark.asyncio
async def test_login_unverified_blocked(client: AsyncClient, clear_mock_codes, multi_user):
    await register_user(client, "unverified@example.com")
    res = await client.post(
        "/api/auth/login",
        json={"email": "unverified@example.com", "password": "secret123"},
    )
    assert res.status_code == 403
    assert res.json()["detail"]["verification_required"] is True


@pytest.mark.asyncio
async def test_login_bad_credentials(client: AsyncClient, clear_mock_codes, multi_user):
    await register_user(client, "badcreds@example.com")
    await verify_user(client, "badcreds@example.com")
    res = await client.post(
        "/api/auth/login",
        json={"email": "badcreds@example.com", "password": "wrongpass"},
    )
    assert res.status_code == 401
