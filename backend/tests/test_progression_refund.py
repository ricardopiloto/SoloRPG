"""Tests for progression refund window (last session XP only)."""

import os
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-min-32-chars")

from app.db.database import async_session
from app.db.models import Campaign, CampaignStatus, GameSession, PlayerCharacter
from app.rules.careers import SKILL_ADVANCE_COST
from app.services.character import (
    get_progression_options,
    purchase_skill_advance,
    purchase_talent,
    refund_progression_purchase,
)
from app.services.session import end_session, start_session
from tests.conftest import auth_headers


async def _seed_character_with_campaign(db):
    character = PlayerCharacter(
        name="Refund Hero",
        attributes={"WS": 35},
        skills=[],
        talents=[],
        xp_total=70,
        xp_spent=0,
    )
    db.add(character)
    await db.flush()
    campaign = Campaign(character_id=character.id, status=CampaignStatus.ACTIVE)
    db.add(campaign)
    await db.commit()
    await db.refresh(character)
    await db.refresh(campaign)
    return character, campaign


@pytest.mark.asyncio
async def test_refund_skill_after_session_end():
    async with async_session() as db:
        character, campaign = await _seed_character_with_campaign(db)
        session = GameSession(campaign_id=campaign.id, duration_minutes=45)
        db.add(session)
        await db.commit()
        await db.refresh(session)

        await end_session(db, session, xp=50)
        await db.refresh(character)

        assert character.progression_source_session_id == session.id
        assert character.progression_refund_budget == 50

        await purchase_skill_advance(db, character.id, "Percepção", "I")
        await db.refresh(character)

        assert character.xp_spent == SKILL_ADVANCE_COST
        purchases = character.progression_purchases
        assert len(purchases) == 1
        assert purchases[0]["refundable_xp"] == SKILL_ADVANCE_COST

        purchase_id = UUID(purchases[0]["id"])
        await refund_progression_purchase(db, character.id, purchase_id)
        await db.refresh(character)

        assert character.xp_spent == 0
        assert character.progression_refund_budget == 50
        assert purchases[0]["refunded"] is True
        assert not any(s.get("name") == "Percepção" for s in character.skills)


@pytest.mark.asyncio
async def test_fifo_budget_exhausted_makes_purchase_non_refundable():
    async with async_session() as db:
        character, campaign = await _seed_character_with_campaign(db)
        session = GameSession(campaign_id=campaign.id, duration_minutes=45)
        db.add(session)
        await db.commit()
        await db.refresh(session)

        await end_session(db, session, xp=50)
        await db.refresh(character)

        for _ in range(10):
            await purchase_skill_advance(db, character.id, "Percepção", "I")

        await db.refresh(character)
        assert character.progression_refund_budget == 0

        await purchase_skill_advance(db, character.id, "Atletismo", "Ag")
        await db.refresh(character)

        last = character.progression_purchases[-1]
        assert last["skill_name"] == "Atletismo"
        assert last["refundable_xp"] == 0

        opts = await get_progression_options(db, character.id)
        assert all(p["skill_name"] != "Atletismo" for p in opts["refundable_purchases"])


@pytest.mark.asyncio
async def test_start_session_closes_refund_window():
    async with async_session() as db:
        character, campaign = await _seed_character_with_campaign(db)
        session = GameSession(campaign_id=campaign.id, duration_minutes=45)
        db.add(session)
        await db.commit()
        await db.refresh(session)

        await end_session(db, session, xp=50)
        await db.refresh(character)

        await purchase_skill_advance(db, character.id, "Percepção", "I")
        await db.refresh(character)
        purchase_id = UUID(character.progression_purchases[0]["id"])

        with patch("app.services.session.probe_image_credits", new_callable=AsyncMock, return_value=False):
            await start_session(db, campaign.id, duration_minutes=45)
        await db.refresh(character)

        assert character.progression_source_session_id is None
        with pytest.raises(ValueError, match="Janela"):
            await refund_progression_purchase(db, character.id, purchase_id)


@pytest.mark.asyncio
async def test_refund_talent():
    async with async_session() as db:
        character, campaign = await _seed_character_with_campaign(db)
        session = GameSession(campaign_id=campaign.id, duration_minutes=45)
        db.add(session)
        await db.commit()
        await db.refresh(session)

        await end_session(db, session, xp=50)
        await db.refresh(character)

        await purchase_talent(db, character.id, "Robusto")
        await db.refresh(character)

        purchase_id = UUID(character.progression_purchases[0]["id"])
        await refund_progression_purchase(db, character.id, purchase_id)
        await db.refresh(character)

        assert character.xp_spent == 0
        assert not any(t.get("name") == "Robusto" for t in character.talents)


@pytest.mark.asyncio
async def test_api_progression_refund_flow(client):
    headers = await auth_headers(client, "refund-api@example.com")
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
    session = session_resp.json()

    async with async_session() as db:
        gs = await db.get(GameSession, UUID(session["id"]))
        char = await db.get(PlayerCharacter, UUID(character["id"]))
        char.xp_total = 20
        await db.commit()
        await end_session(db, gs, xp=50)

    prog = await client.get(
        f"/api/characters/{character['id']}/progression", headers=headers
    )
    assert prog.json()["progression_window_active"] is True
    assert prog.json()["refund_budget_total"] == 50

    buy = await client.post(
        f"/api/characters/{character['id']}/progression/skill",
        json={"skill_name": "Percepção", "linked_attribute": "I"},
        headers=headers,
    )
    assert buy.status_code == 200

    prog2 = await client.get(
        f"/api/characters/{character['id']}/progression", headers=headers
    )
    purchase = prog2.json()["refundable_purchases"][0]

    refund = await client.post(
        f"/api/characters/{character['id']}/progression/refund",
        json={"purchase_id": purchase["id"]},
        headers=headers,
    )
    assert refund.status_code == 200
    assert refund.json()["xp_spent"] == 0

    prog3 = await client.get(
        f"/api/characters/{character['id']}/progression", headers=headers
    )
    assert prog3.json()["refundable_purchases"] == []
    assert prog3.json()["xp_available"] == 70
