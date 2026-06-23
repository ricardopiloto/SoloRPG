import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, register_user, verify_user


@pytest.mark.asyncio
async def test_characters_require_auth(client: AsyncClient):
    res = await client.get("/api/characters")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_list_characters_scoped_to_user(client: AsyncClient, clear_mock_codes, multi_user):
    headers_a = await auth_headers(client, "usera@example.com")
    chars_a = await client.get("/api/characters", headers=headers_a)
    assert chars_a.status_code == 200
    assert len(chars_a.json()) == 1  # starter

    headers_b = await auth_headers(client, "userb@example.com")
    chars_b = await client.get("/api/characters", headers=headers_b)
    assert len(chars_b.json()) == 1
    assert chars_a.json()[0]["id"] != chars_b.json()[0]["id"]


@pytest.mark.asyncio
async def test_cross_user_character_forbidden(client: AsyncClient, clear_mock_codes, multi_user):
    headers_a = await auth_headers(client, "ownera@example.com")
    char_id = (await client.get("/api/characters", headers=headers_a)).json()[0]["id"]

    headers_b = await auth_headers(client, "ownerb@example.com")
    res = await client.get(f"/api/characters/{char_id}", headers=headers_b)
    assert res.status_code == 403
