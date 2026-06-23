import os

import pytest

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from sqlalchemy import select

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, CharacterStatus, GameSession, PlayerCharacter, SessionTurn
from app.rules.fate import spend_fortune_point
from app.services.campaign import create_campaign, get_active_session, mark_campaign_completed
from app.services.character import get_progression_options
from app.services.memory import persist_session_summary
from app.services.session import append_turn, start_session


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _seed_character(db):
    char = PlayerCharacter(name="Hero", status=CharacterStatus.ALIVE, attributes={"Ag": 35})
    db.add(char)
    await db.commit()
    await db.refresh(char)
    return char


@pytest.mark.asyncio
async def test_create_campaign_blocks_duplicate_active():
    async with async_session() as db:
        char = await _seed_character(db)
        await create_campaign(db, char.id)
        with pytest.raises(ValueError, match="campanha ativa"):
            await create_campaign(db, char.id)


@pytest.mark.asyncio
async def test_create_campaign_rejects_dead_character():
    async with async_session() as db:
        char = PlayerCharacter(name="Dead", status=CharacterStatus.DEAD)
        db.add(char)
        await db.commit()
        await db.refresh(char)
        with pytest.raises(ValueError, match="morto"):
            await create_campaign(db, char.id)


@pytest.mark.asyncio
async def test_active_session_and_resume():
    async with async_session() as db:
        char = await _seed_character(db)
        campaign = await create_campaign(db, char.id)
        session = await start_session(db, campaign.id)
        active = await get_active_session(db, campaign.id)
        assert active is not None
        assert active.id == session.id


@pytest.mark.asyncio
async def test_mark_campaign_completed():
    async with async_session() as db:
        char = await _seed_character(db)
        campaign = await create_campaign(db, char.id)
        completed = await mark_campaign_completed(db, campaign.id)
        assert completed.status == CampaignStatus.COMPLETED


@pytest.mark.asyncio
async def test_progression_options_lists_skills_and_talents():
    async with async_session() as db:
        char = await _seed_character(db)
        char.xp_total = 50
        await db.commit()
        opts = await get_progression_options(db, char.id)
        assert opts["xp_available"] == 50
        assert len(opts["skills"]) >= 5
        assert len(opts["talents"]) >= 3
        assert opts["skills"][0]["affordable"] is True


@pytest.mark.asyncio
async def test_api_complete_campaign(client):
    from tests.conftest import seed_user_character

    async with async_session() as db:
        user, char, headers = await seed_user_character(db, "complete-api@example.com")
        campaign = await create_campaign(db, char.id)
        response = await client.post(
            f"/api/campaigns/{campaign.id}/complete", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "concluida"


@pytest.mark.asyncio
async def test_api_active_session(client):
    from tests.conftest import seed_user_character

    async with async_session() as db:
        user, char, headers = await seed_user_character(db, "active-api@example.com")
        campaign = await create_campaign(db, char.id)
        session = await start_session(db, campaign.id)
        response = await client.get(
            f"/api/campaigns/{campaign.id}/active-session", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(session.id)


@pytest.mark.asyncio
async def test_persist_session_summary_updates_social_perception():
    async with async_session() as db:
        char = await _seed_character(db)
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()
        await db.refresh(campaign)

        await persist_session_summary(
            db,
            campaign,
            session,
            "Resumo jogador",
            {"percepcao_social": "Temido nas docas de Altdorf", "eventos_principais": []},
        )
        await db.refresh(char)
        assert char.social_perception == "Temido nas docas de Altdorf"


@pytest.mark.asyncio
async def test_append_turn_persists_session_turn_row():
    async with async_session() as db:
        char = await _seed_character(db)
        campaign = await create_campaign(db, char.id)
        session = await start_session(db, campaign.id)
        await append_turn(db, session, "player", "Entro na taverna")
        turns = (
            await db.scalars(
                select(SessionTurn).where(SessionTurn.session_id == session.id)
            )
        ).all()
        assert len(turns) == 1
        assert turns[0].content == "Entro na taverna"


def test_spend_fortune_point_reroll():
    result = spend_fortune_point(2, "reroll")
    assert result.success
    assert result.fortune_remaining == 1


def test_spend_fortune_point_rejects_bonus():
    result = spend_fortune_point(2, "bonus_teste")
    assert not result.success
    assert result.fortune_remaining == 2


def test_spend_fortune_point_empty():
    result = spend_fortune_point(0)
    assert not result.success
