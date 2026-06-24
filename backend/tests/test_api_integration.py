"""API integration tests — full HTTP lifecycle with mock LLM."""

import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("EMAIL_PROVIDER", "mock")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-min-32-chars")

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_api_character_campaign_session_lifecycle(client):
    headers = await auth_headers(client, "lifecycle@example.com")
    pregen = await client.post(
        "/api/characters/pregen", json={"template_index": 0}, headers=headers
    )
    assert pregen.status_code == 200
    character = pregen.json()
    assert character["name"]
    assert character["status"] == "vivo"

    chars = await client.get("/api/characters", headers=headers)
    assert chars.status_code == 200
    assert any(c["id"] == character["id"] for c in chars.json())

    campaign_resp = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}, headers=headers
    )
    assert campaign_resp.status_code == 200
    campaign = campaign_resp.json()
    assert campaign["status"] == "ativa"

    dup = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}, headers=headers
    )
    assert dup.status_code == 400

    session_resp = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
        headers=headers,
    )
    assert session_resp.status_code == 200
    session = session_resp.json()
    assert session["is_active"] is True

    active = await client.get(
        f"/api/campaigns/{campaign['id']}/active-session", headers=headers
    )
    assert active.status_code == 200
    assert active.json()["id"] == session["id"]

    detail = await client.get(f"/api/sessions/{session['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["campaign_id"] == campaign["id"]

    mock_text = (
        'A névoa paira sobre o cais.\n[TESTE]{"tipo":"teste_atributo","atributo":"Ag",'
        '"pericia":"Atletismo","modificador":0}[/TESTE]'
    )
    with patch("app.api.routes.gm.llm.complete", new_callable=AsyncMock, return_value=mock_text):
        turn = await client.post(
            f"/api/sessions/{session['id']}/turn",
            json={"action": "Avanço cautelosamente"},
            headers=headers,
        )
    assert turn.status_code == 200
    body = turn.json()
    assert body["turn_phase"] == "awaiting_roll"
    assert body["pending_test"] is not None

    roll = await client.post(
        f"/api/sessions/{session['id']}/roll", json={}, headers=headers
    )
    assert roll.status_code == 200
    assert roll.json()["roll_results"]
    assert roll.json()["turn_phase"] == "awaiting_narrate"

    with patch(
        "app.api.routes.gm.llm.complete",
        new_callable=AsyncMock,
        return_value="Você consegue passar.",
    ):
        narrate = await client.post(
            f"/api/sessions/{session['id']}/roll/narrate", json={}, headers=headers
        )
    assert narrate.status_code == 200
    assert narrate.json()["narrative"]


@pytest.mark.asyncio
async def test_api_progression_after_xp(client):
    headers = await auth_headers(client, "progression@example.com")
    pregen = await client.post(
        "/api/characters/pregen", json={"template_index": 1}, headers=headers
    )
    character = pregen.json()

    from uuid import UUID

    from app.db.database import async_session
    from app.db.models import PlayerCharacter

    async with async_session() as db:
        char = await db.get(PlayerCharacter, UUID(character["id"]))
        char.xp_total = 20
        await db.commit()

    prog = await client.get(
        f"/api/characters/{character['id']}/progression", headers=headers
    )
    assert prog.status_code == 200
    data = prog.json()
    assert data["xp_available"] == 20
    assert len(data["skills"]) > 0

    buy = await client.post(
        f"/api/characters/{character['id']}/progression/skill",
        json={"skill_name": "Atletismo", "linked_attribute": "Ag"},
        headers=headers,
    )
    assert buy.status_code == 200
    assert buy.json()["xp_spent"] == 5


@pytest.mark.asyncio
async def test_api_progression_skill_advances_accumulate(client):
    headers = await auth_headers(client, "progression-multi@example.com")
    pregen = await client.post(
        "/api/characters/pregen", json={"template_index": 0}, headers=headers
    )
    character = pregen.json()

    from uuid import UUID

    from app.db.database import async_session
    from app.db.models import PlayerCharacter

    async with async_session() as db:
        char = await db.get(PlayerCharacter, UUID(character["id"]))
        char.xp_total = 50
        await db.commit()

    for _ in range(4):
        resp = await client.post(
            f"/api/characters/{character['id']}/progression/skill",
            json={"skill_name": "Percepção", "linked_attribute": "I"},
            headers=headers,
        )
        assert resp.status_code == 200

    async with async_session() as db:
        char = await db.get(PlayerCharacter, UUID(character["id"]))
        perc = next(s for s in char.skills if s["name"] == "Percepção")
        assert perc["advances"] == 4
        assert char.xp_spent == 20

    prog = await client.get(
        f"/api/characters/{character['id']}/progression", headers=headers
    )
    assert prog.status_code == 200
    perc_opt = next(s for s in prog.json()["skills"] if s["name"] == "Percepção")
    assert perc_opt["current_advances"] == 4
    assert prog.json()["xp_available"] == 30


@pytest.mark.asyncio
async def test_api_session_pause_resume(client):
    """Sessão pode ser pausada, retomada, e não cria duplicata enquanto pausada."""
    headers = await auth_headers(client, "pause@example.com")
    pregen = await client.post(
        "/api/characters/pregen", json={"template_index": 0}, headers=headers
    )
    character = pregen.json()
    campaign_resp = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}, headers=headers
    )
    campaign = campaign_resp.json()

    session_resp = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
        headers=headers,
    )
    assert session_resp.status_code == 200
    session = session_resp.json()
    session_id = session["id"]
    assert session["paused_at"] is None

    pause_resp = await client.post(
        f"/api/sessions/{session_id}/pause", headers=headers
    )
    assert pause_resp.status_code == 200
    paused = pause_resp.json()
    assert paused["paused_at"] is not None
    assert paused["time_remaining_minutes"] >= 44

    dup_pause = await client.post(
        f"/api/sessions/{session_id}/pause", headers=headers
    )
    assert dup_pause.status_code == 400

    start_again = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
        headers=headers,
    )
    assert start_again.status_code == 200
    assert start_again.json()["id"] == session_id

    resume_resp = await client.post(
        f"/api/sessions/{session_id}/resume", headers=headers
    )
    assert resume_resp.status_code == 200
    resumed = resume_resp.json()
    assert resumed["paused_at"] is None
    assert resumed["time_remaining_minutes"] >= 44

    dup_resume = await client.post(
        f"/api/sessions/{session_id}/resume", headers=headers
    )
    assert dup_resume.status_code == 400


@pytest.mark.asyncio
async def test_api_session_history(client):
    """GET /sessions/{id}/history retorna turns persistidos em ordem."""
    headers = await auth_headers(client, "history@example.com")
    pregen = await client.post(
        "/api/characters/pregen", json={"template_index": 1}, headers=headers
    )
    character = pregen.json()
    campaign_resp = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}, headers=headers
    )
    campaign = campaign_resp.json()
    session_resp = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
        headers=headers,
    )
    session_id = session_resp.json()["id"]

    with patch(
        "app.api.routes.gm.llm.complete",
        new_callable=AsyncMock,
        return_value="O mestre narra algo.",
    ):
        await client.post(
            f"/api/sessions/{session_id}/turn",
            json={"action": "Olho ao redor"},
            headers=headers,
        )

    history_resp = await client.get(
        f"/api/sessions/{session_id}/history", headers=headers
    )
    assert history_resp.status_code == 200
    turns = history_resp.json()
    assert len(turns) >= 2
    roles = [t["role"] for t in turns]
    assert "player" in roles
    assert "gm" in roles


@pytest.mark.asyncio
async def test_api_campaign_complete(client):
    headers = await auth_headers(client, "complete@example.com")
    pregen = await client.post(
        "/api/characters/pregen", json={"template_index": 0}, headers=headers
    )
    character = pregen.json()
    campaign_resp = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}, headers=headers
    )
    campaign = campaign_resp.json()

    complete = await client.post(
        f"/api/campaigns/{campaign['id']}/complete", headers=headers
    )
    assert complete.status_code == 200
    assert complete.json()["status"] == "concluida"

    list_resp = await client.get("/api/campaigns", headers=headers)
    statuses = [c["status"] for c in list_resp.json() if c["id"] == campaign["id"]]
    assert statuses == ["concluida"]


@pytest.mark.asyncio
async def test_api_list_careers_returns_class_field(client):
    resp = await client.get("/api/rules/careers?tier=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["careers"]) >= 1
    assert data["careers"][0]["class"] in ("martial", "academic", "ranger", "rogue")


@pytest.mark.asyncio
async def test_api_wizard_character_creation(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "enable_custom_chargen", True)
    from app.rules.character_creation import roll_all_characteristics

    headers = await auth_headers(client, "wizard@example.com")

    career_skills = {
        "Luta": 8,
        "Atletismo": 6,
        "Percepção": 5,
        "Vontade": 5,
        "Intimidação": 4,
        "Orientação": 4,
        "Atirar (Armas de Fogo)": 4,
        "Charme": 4,
    }
    draft = {
        "species_id": "human",
        "species_method": "choose",
        "career_id": "soldado",
        "career_method": "choose",
        "attributes_method": "roll",
        "attribute_rolls": roll_all_characteristics(),
        "fate_allotted": 2,
        "species_skills": {"Charme": 3},
        "career_skills": career_skills,
        "career_talent": "Resolução",
        "species_talents": ["Sortudo"],
        "name": "API Wizard Hero",
        "background": "Teste integração",
    }
    resp = await client.post(
        "/api/characters", json={"draft": draft}, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "API Wizard Hero"
    assert data["wounds_max"] >= 1
    assert data["careers"][0]["name"] == "Soldado"

    legacy = await client.post(
        "/api/characters",
        json={"name": "Legacy", "attributes": {}, "wounds_max": 99},
        headers=headers,
    )
    assert legacy.status_code == 422
