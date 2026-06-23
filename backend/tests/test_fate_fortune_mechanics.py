import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, GameSession, PlayerCharacter
from app.rules.fate import spend_fate_point, spend_fortune_point
from app.services.gm_orchestrator import GMOrchestrator
from app.services.session import start_session


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _seed_campaign(db, fate_current=3, fortune_current=0):
    character = PlayerCharacter(
        name="Test Hero",
        attributes={"Ag": 35},
        fate_current=fate_current,
        fate_max=3,
        fortune_current=fortune_current,
        fortune_max=fortune_current,
    )
    db.add(character)
    await db.flush()
    campaign = Campaign(character_id=character.id, status=CampaignStatus.ACTIVE)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    await db.refresh(character)
    return campaign, character


@pytest.mark.asyncio
async def test_start_session_refreshes_fortune_from_fate():
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fate_current=3, fortune_current=0)
        with patch("app.services.session.probe_image_credits", new_callable=AsyncMock, return_value=False):
            await start_session(db, campaign.id)
        await db.refresh(character)
        assert character.fortune_current == 3
        assert character.fortune_max == 3


@pytest.mark.asyncio
async def test_paused_session_does_not_refresh_fortune():
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fate_current=2, fortune_current=1)
        paused = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            paused_at=datetime.now(timezone.utc),
        )
        db.add(paused)
        await db.commit()
        with patch("app.services.session.probe_image_credits", new_callable=AsyncMock) as probe:
            session = await start_session(db, campaign.id)
            probe.assert_not_called()
        assert session.id == paused.id
        await db.refresh(character)
        assert character.fortune_current == 1


@pytest.mark.asyncio
async def test_fortune_reroll_spends_and_re_rolls():
    gm = GMOrchestrator()
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fate_current=2, fortune_current=2)
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_narrate",
            pending_roll_result={
                "roll_results": [{"type": "test", "roll": 90, "target": 35, "success": False, "llm_text": "fail"}],
                "roll_texts": ["fail"],
                "setup_narrative": "setup",
                "payloads": [{"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0}],
                "wounds_before": character.wounds_current,
            },
        )
        db.add(session)
        await db.commit()

        with patch.object(gm, "_resolve_test_signal", return_value={
            "type": "test", "roll": 10, "target": 35, "success": True, "llm_text": "ok"
        }):
            result = await gm.execute_fortune_reroll(db, session.id, roll_override=10)

        await db.refresh(character)
        assert character.fortune_current == 1
        assert result.roll_results[0]["success"] is True


@pytest.mark.asyncio
async def test_fortune_reroll_rejects_without_failed_roll():
    gm = GMOrchestrator()
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fortune_current=2)
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_narrate",
            pending_roll_result={
                "roll_results": [{"type": "test", "roll": 10, "target": 35, "success": True, "llm_text": "ok"}],
                "roll_texts": ["ok"],
                "setup_narrative": "setup",
                "payloads": [{"tipo": "teste_atributo", "atributo": "Ag"}],
                "wounds_before": 0,
            },
        )
        db.add(session)
        await db.commit()

        with pytest.raises(ValueError, match="Fortuna não aplicável"):
            await gm.execute_fortune_reroll(db, session.id, roll_override=50)


@pytest.mark.asyncio
async def test_fortune_reroll_rejects_second_reroll_on_same_test():
    gm = GMOrchestrator()
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fortune_current=2)
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_narrate",
            pending_roll_result={
                "roll_results": [{"type": "test", "roll": 90, "target": 35, "success": False, "llm_text": "fail"}],
                "roll_texts": ["fail"],
                "setup_narrative": "setup",
                "payloads": [{"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0}],
                "wounds_before": character.wounds_current,
                "fortune_reroll_used": True,
            },
        )
        db.add(session)
        await db.commit()

        with pytest.raises(ValueError, match="Fortuna já usada"):
            await gm.execute_fortune_reroll(db, session.id, roll_override=50)

        await db.refresh(character)
        assert character.fortune_current == 2


@pytest.mark.asyncio
async def test_fortune_reroll_available_after_first_failure():
    from app.api.routes import _roll_response

    gm = GMOrchestrator()
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fortune_current=2)
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_roll",
            pending_test={
                "payload": {"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0},
                "setup_narrative": "setup",
            },
        )
        db.add(session)
        await db.commit()

        with patch.object(gm, "_resolve_test_signal", return_value={
            "type": "test", "roll": 90, "target": 35, "success": False, "llm_text": "fail"
        }):
            result = await gm.execute_roll(db, session.id, roll_override=90)

        await db.refresh(session)
        response = _roll_response(result, session, character)
        assert response.fortune_reroll_available is True


@pytest.mark.asyncio
async def test_fortune_reroll_unavailable_after_reroll_used():
    from app.api.routes import _roll_response

    gm = GMOrchestrator()
    async with async_session() as db:
        campaign, character = await _seed_campaign(db, fortune_current=1)
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_narrate",
            pending_roll_result={
                "roll_results": [{"type": "test", "roll": 90, "target": 35, "success": False, "llm_text": "fail"}],
                "roll_texts": ["fail"],
                "setup_narrative": "setup",
                "payloads": [{"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0}],
                "wounds_before": character.wounds_current,
            },
        )
        db.add(session)
        await db.commit()

        with patch.object(gm, "_resolve_test_signal", return_value={
            "type": "test", "roll": 95, "target": 35, "success": False, "llm_text": "fail again"
        }):
            result = await gm.execute_fortune_reroll(db, session.id, roll_override=95)

        await db.refresh(session)
        await db.refresh(character)
        response = _roll_response(result, session, character)
        assert response.fortune_reroll_available is False
        assert character.fortune_current == 0


def test_avoid_wound_keeps_wounds():
    result = spend_fate_point(2, 8, 12, "avoid_wound")
    assert result.success
    assert result.wounds_after == 8
    assert result.fate_remaining == 1


def test_avoid_death_sets_one_wound():
    result = spend_fate_point(2, 0, 12, "avoid_death")
    assert result.success
    assert result.wounds_after == 1


def test_fortune_unavailable_blocks_reroll():
    result = spend_fortune_point(0, "reroll")
    assert not result.success
