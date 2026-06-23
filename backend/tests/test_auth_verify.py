import pytest
from httpx import AsyncClient

from tests.conftest import register_user, verify_user


@pytest.mark.asyncio
async def test_verify_success_creates_starter(client: AsyncClient, clear_mock_codes, multi_user):
    await register_user(client, "verify@example.com")
    data = await verify_user(client, "verify@example.com")
    assert data["access_token"]
    assert data["user"]["email_verified"] is True
    assert data["starter_character"] is not None
    assert data["starter_character"]["name"]


@pytest.mark.asyncio
async def test_verify_wrong_code(client: AsyncClient, clear_mock_codes, multi_user):
    await register_user(client, "wrong@example.com")
    res = await client.post(
        "/api/auth/verify-email",
        json={"email": "wrong@example.com", "code": "00000000"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_resend_verification(client: AsyncClient, clear_mock_codes, multi_user):
    from app.email.adapter import mock_sent_codes

    await register_user(client, "resend@example.com")
    first = mock_sent_codes["resend@example.com"]
    res = await client.post("/api/auth/resend-verification", json={"email": "resend@example.com"})
    assert res.status_code == 200
    second = mock_sent_codes["resend@example.com"]
    assert second != first

    res2 = await client.post("/api/auth/resend-verification", json={"email": "resend@example.com"})
    assert res2.status_code == 400
