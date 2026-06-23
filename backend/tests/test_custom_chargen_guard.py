import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_wizard_endpoints_blocked_when_flag_off(client: AsyncClient):
    headers = await auth_headers(client, "chargen-off@example.com")
    draft = {"draft": {"species_id": "human", "name": "Test"}}

    endpoints = [
        ("POST", "/api/characters/validate-creation", draft),
        ("POST", "/api/characters/creation/roll-attributes", {}),
        ("POST", "/api/characters/creation/roll-career", draft),
        ("POST", "/api/characters/creation/roll-species-talent", draft),
        (
            "POST",
            "/api/characters/generate-background",
            {"name": "X", "career": "Soldado"},
        ),
        ("POST", "/api/characters", draft),
    ]

    for method, path, body in endpoints:
        res = await client.request(method, path, json=body, headers=headers)
        assert res.status_code == 403, f"{method} {path} should be 403, got {res.status_code}"


@pytest.mark.asyncio
async def test_pregen_works_when_flag_off(client: AsyncClient):
    headers = await auth_headers(client, "pregen-ok@example.com")
    listing = await client.get("/api/characters/pregen", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) >= 1

    create = await client.post(
        "/api/characters/pregen", json={"template_index": 0}, headers=headers
    )
    assert create.status_code == 200


@pytest.mark.asyncio
async def test_wizard_allowed_when_flag_on(client: AsyncClient, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "enable_custom_chargen", True)
    headers = await auth_headers(client, "chargen-on@example.com")

    roll = await client.post("/api/characters/creation/roll-attributes", headers=headers)
    assert roll.status_code == 200
    assert "attributes" in roll.json()
