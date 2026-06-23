import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, clear_mock_codes, multi_user):
    res = await client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "password1", "password_confirm": "password1"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "new@example.com"
    assert data["verification_required"] is True


@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient, multi_user):
    res = await client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "password1", "password_confirm": "other123"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient, multi_user):
    res = await client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "short", "password_confirm": "short"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient, multi_user):
    res = await client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password1", "password_confirm": "password1"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, clear_mock_codes, multi_user):
    payload = {"email": "dup@example.com", "password": "password1", "password_confirm": "password1"}
    assert (await client.post("/api/auth/register", json=payload)).status_code == 201
    res = await client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
