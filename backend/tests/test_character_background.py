import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_generate_background_mock():
    from app.services.character_background import generate_background

    text = await generate_background({"name": "Helena", "career": "Soldado"})
    assert "Helena" in text
    assert "Soldado" in text


@pytest.mark.asyncio
async def test_generate_background_requires_name():
    from app.services.character_background import generate_background

    with pytest.raises(ValueError, match="obrigat"):
        await generate_background({"name": "", "career": "Soldado"})


@pytest.mark.asyncio
async def test_api_generate_background(client: AsyncClient, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "enable_custom_chargen", True)
    headers = await auth_headers(client, "bg@example.com")
    resp = await client.post(
        "/api/characters/generate-background",
        json={"name": "Tobias", "career": "Aprendiz", "hints": "expulso da academia"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert "Tobias" in resp.json()["background"]

    bad = await client.post(
        "/api/characters/generate-background",
        json={"name": "", "career": "X"},
        headers=headers,
    )
    assert bad.status_code == 400
