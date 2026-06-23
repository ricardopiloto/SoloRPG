import os

import pytest

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from sqlalchemy import select

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, CharacterStatus, GameSession, NPC, PlayerCharacter
from app.services.campaign import apply_nova_campanha, create_campaign, list_campaign_npcs
from app.services.memory import persist_session_summary


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_apply_nova_campanha_sets_npc_met_location():
    async with async_session() as db:
        char = PlayerCharacter(name="Hero", status=CharacterStatus.ALIVE)
        db.add(char)
        await db.commit()
        await db.refresh(char)
        campaign = await create_campaign(db, char.id)

        await apply_nova_campanha(
            db,
            campaign,
            {
                "tom": "sombrio",
                "localizacao_abertura": "Estalagem do Corvo",
                "npcs_iniciais": [
                    {"nome": "Greta", "papel": "Estalajadeira", "nome_conhecido": "Greta, a estalajadeira"},
                ],
            },
        )

        npcs = await list_campaign_npcs(db, campaign.id)
        assert len(npcs) == 1
        assert npcs[0].known_name == "Greta, a estalajadeira"
        assert npcs[0].met_location == "Estalagem do Corvo"


@pytest.mark.asyncio
async def test_persist_session_summary_npc_local_and_known_name():
    async with async_session() as db:
        char = PlayerCharacter(name="Hero", status=CharacterStatus.ALIVE)
        db.add(char)
        await db.flush()
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
            "Resumo",
            {
                "eventos_principais": [],
                "npcs_interagidos": [
                    {
                        "nome": "Hans",
                        "nome_conhecido": "Hans Gruber",
                        "local": "Praça do Mercado",
                        "status_relacao": "neutro",
                    }
                ],
            },
        )

        npc = await db.scalar(select(NPC).where(NPC.campaign_id == campaign.id, NPC.name == "Hans"))
        assert npc is not None
        assert npc.known_name == "Hans Gruber"
        assert npc.met_location == "Praça do Mercado"


@pytest.mark.asyncio
async def test_api_list_campaign_npcs(client):
    from tests.conftest import seed_user_character

    async with async_session() as db:
        user, char, headers = await seed_user_character(db, "npc-api@example.com")
        campaign = await create_campaign(db, char.id)
        await apply_nova_campanha(
            db,
            campaign,
            {
                "localizacao_abertura": "Docas",
                "npcs_iniciais": [{"nome": "Karl", "papel": "Guarda"}],
            },
        )

        response = await client.get(f"/api/campaigns/{campaign.id}/npcs", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["npcs"]) == 1
        assert data["npcs"][0]["name"] == "Karl"
        assert data["npcs"][0]["met_location"] == "Docas"
