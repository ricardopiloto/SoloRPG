import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, GameSession, PlayerCharacter, SessionMode
from app.services.gm_orchestrator import GMOrchestrator


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_quick_roll_attribute():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(
            name="Test",
            attributes={"Ag": 40, "WS": 35},
            wounds_max=10,
            fate_max=2,
        )
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True, mode=SessionMode.EXPLORATION)
        db.add(session)
        await db.commit()

        result = await gm.execute_quick_roll(db, session.id, "attribute", "Ag", 10)
        assert result.roll_type == "attribute"
        assert result.key == "Ag"
        assert result.modifier == 10
        assert result.target == 50
        assert 1 <= result.roll <= 100


@pytest.mark.asyncio
async def test_quick_roll_blocked_during_pending_test():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Test", attributes={"Ag": 40})
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_roll",
            pending_test={"payload": {}},
        )
        db.add(session)
        await db.commit()

        with pytest.raises(ValueError, match="teste do GM"):
            await gm.execute_quick_roll(db, session.id, "attribute", "Ag", 0)


@pytest.mark.asyncio
async def test_quick_roll_skill_with_modifier():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(
            name="Test",
            attributes={"Ag": 35},
            skills=[{"name": "Atletismo", "advances": 2}],
        )
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        result = await gm.execute_quick_roll(db, session.id, "skill", "Atletismo", -5)
        assert result.key == "Atletismo"
        assert result.target == 32  # 35 + 2 - 5


@pytest.mark.asyncio
async def test_quick_roll_unowned_skill():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(
            name="Test",
            attributes={"S": 38},
            skills=[],
        )
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        result = await gm.execute_quick_roll(db, session.id, "skill", "Escalar", 0)
        assert result.key == "Escalar"
        assert result.target == 38  # S + 0 advances


@pytest.mark.asyncio
async def test_quick_roll_invalid_skill():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Test", attributes={"Ag": 40})
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        with pytest.raises(ValueError, match="inválida"):
            await gm.execute_quick_roll(db, session.id, "skill", "Perícia Inexistente", 0)


@pytest.mark.asyncio
async def test_quick_roll_intuicao_skill():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(
            name="Test",
            attributes={"I": 33},
            skills=[{"name": "Intuição", "advances": 1}],
        )
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        result = await gm.execute_quick_roll(db, session.id, "skill", "Intuição", 0)
        assert result.key == "Intuição"
        assert result.target == 34  # I 33 + 1 advance
