"""API integration tests — full HTTP lifecycle with mock LLM."""

import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("DATABASE_PROFILE", "sqlite-dev")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("LLM_PROVIDER", "mock")

from app.db.database import engine
from app.db.models import Base


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_api_character_campaign_session_lifecycle(client):
    pregen = await client.post("/api/characters/pregen", json={"template_index": 0})
    assert pregen.status_code == 200
    character = pregen.json()
    assert character["name"]
    assert character["status"] == "vivo"

    chars = await client.get("/api/characters")
    assert chars.status_code == 200
    assert any(c["id"] == character["id"] for c in chars.json())

    campaign_resp = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}
    )
    assert campaign_resp.status_code == 200
    campaign = campaign_resp.json()
    assert campaign["status"] == "ativa"

    dup = await client.post("/api/campaigns", json={"character_id": character["id"]})
    assert dup.status_code == 400

    session_resp = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
    )
    assert session_resp.status_code == 200
    session = session_resp.json()
    assert session["is_active"] is True

    active = await client.get(f"/api/campaigns/{campaign['id']}/active-session")
    assert active.status_code == 200
    assert active.json()["id"] == session["id"]

    detail = await client.get(f"/api/sessions/{session['id']}")
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
        )
    assert turn.status_code == 200
    body = turn.json()
    assert body["turn_phase"] == "awaiting_roll"
    assert body["pending_test"] is not None

    roll = await client.post(f"/api/sessions/{session['id']}/roll", json={})
    assert roll.status_code == 200
    assert roll.json()["roll_results"]
    assert roll.json()["turn_phase"] == "awaiting_narrate"

    with patch("app.api.routes.gm.llm.complete", new_callable=AsyncMock, return_value="Você consegue passar."):
        narrate = await client.post(f"/api/sessions/{session['id']}/roll/narrate", json={})
    assert narrate.status_code == 200
    assert narrate.json()["narrative"]


@pytest.mark.asyncio
async def test_api_progression_after_xp(client):
    pregen = await client.post("/api/characters/pregen", json={"template_index": 1})
    character = pregen.json()

    from uuid import UUID

    from app.db.database import async_session
    from app.db.models import PlayerCharacter

    async with async_session() as db:
        char = await db.get(PlayerCharacter, UUID(character["id"]))
        char.xp_total = 20
        await db.commit()

    prog = await client.get(f"/api/characters/{character['id']}/progression")
    assert prog.status_code == 200
    data = prog.json()
    assert data["xp_available"] == 20
    assert len(data["skills"]) > 0

    buy = await client.post(
        f"/api/characters/{character['id']}/progression/skill",
        json={"skill_name": "Atletismo", "linked_attribute": "Ag"},
    )
    assert buy.status_code == 200
    assert buy.json()["xp_spent"] == 5


@pytest.mark.asyncio
async def test_api_session_pause_resume(client):
    """Sessão pode ser pausada, retomada, e não cria duplicata enquanto pausada."""
    pregen = await client.post("/api/characters/pregen", json={"template_index": 0})
    character = pregen.json()
    campaign_resp = await client.post("/api/campaigns", json={"character_id": character["id"]})
    campaign = campaign_resp.json()

    session_resp = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
    )
    assert session_resp.status_code == 200
    session = session_resp.json()
    session_id = session["id"]
    assert session["paused_at"] is None

    # Pause
    pause_resp = await client.post(f"/api/sessions/{session_id}/pause")
    assert pause_resp.status_code == 200
    paused = pause_resp.json()
    assert paused["paused_at"] is not None
    # Timer should be frozen (same time_remaining as fresh session, roughly)
    assert paused["time_remaining_minutes"] >= 44

    # Trying to pause again should fail
    dup_pause = await client.post(f"/api/sessions/{session_id}/pause")
    assert dup_pause.status_code == 400

    # Starting a new session for same campaign should return the paused one
    start_again = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
    )
    assert start_again.status_code == 200
    assert start_again.json()["id"] == session_id

    # Resume
    resume_resp = await client.post(f"/api/sessions/{session_id}/resume")
    assert resume_resp.status_code == 200
    resumed = resume_resp.json()
    assert resumed["paused_at"] is None
    # total_paused_seconds visible via detail; time remaining should still be ~45
    assert resumed["time_remaining_minutes"] >= 44

    # Trying to resume again should fail
    dup_resume = await client.post(f"/api/sessions/{session_id}/resume")
    assert dup_resume.status_code == 400


@pytest.mark.asyncio
async def test_api_session_history(client):
    """GET /sessions/{id}/history retorna turns persistidos em ordem."""
    pregen = await client.post("/api/characters/pregen", json={"template_index": 1})
    character = pregen.json()
    campaign_resp = await client.post("/api/campaigns", json={"character_id": character["id"]})
    campaign = campaign_resp.json()
    session_resp = await client.post(
        f"/api/campaigns/{campaign['id']}/sessions",
        json={"duration_minutes": 45},
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
        )

    history_resp = await client.get(f"/api/sessions/{session_id}/history")
    assert history_resp.status_code == 200
    turns = history_resp.json()
    # Should have at least the player turn and gm turn
    assert len(turns) >= 2
    roles = [t["role"] for t in turns]
    assert "player" in roles
    assert "gm" in roles


@pytest.mark.asyncio
async def test_api_campaign_complete(client):
    pregen = await client.post("/api/characters/pregen", json={"template_index": 0})
    character = pregen.json()
    campaign_resp = await client.post(
        "/api/campaigns", json={"character_id": character["id"]}
    )
    campaign = campaign_resp.json()

    complete = await client.post(f"/api/campaigns/{campaign['id']}/complete")
    assert complete.status_code == 200
    assert complete.json()["status"] == "concluida"

    list_resp = await client.get("/api/campaigns")
    statuses = [c["status"] for c in list_resp.json() if c["id"] == campaign["id"]]
    assert statuses == ["concluida"]
