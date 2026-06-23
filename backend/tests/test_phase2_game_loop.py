import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, GameSession, PlayerCharacter, SessionMode
from app.llm.signals import parse_signals
from app.services.gm_orchestrator import GMOrchestrator
from app.services.session import enter_combat


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=__import__("app.main", fromlist=["app"]).app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_parse_teste_signal():
    text = (
        'Cena tensa.\n[TESTE]{"tipo":"teste_atributo","atributo":"Ag","pericia":"Atletismo","modificador":-10}'
        '[/TESTE]\nO que você faz?'
    )
    parsed = parse_signals(text)
    assert any(s.tag == "TESTE" for s in parsed.signals)
    assert "Cena tensa" in parsed.narrative


@pytest.mark.asyncio
async def test_pending_test_blocks_turn_until_roll():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Test", attributes={"Ag": 35}, wounds_max=10, fate_max=2)
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True, mode=SessionMode.EXPLORATION)
        db.add(session)
        await db.commit()

        llm_response = (
            'Você avança.\n[TESTE]{"tipo":"teste_atributo","atributo":"Ag","pericia":"Atletismo","modificador":0}'
            "[/TESTE]"
        )

        with patch.object(gm.llm, "complete", new_callable=AsyncMock, return_value=llm_response):
            result = await gm.process_turn(db, session.id, "Corro para a porta")

        assert result.pending_test is not None
        assert result.roll_results == []
        await db.refresh(session)
        assert session.turn_phase == "awaiting_roll"

        with pytest.raises(ValueError, match="Rolagem pendente"):
            await gm.process_turn(db, session.id, "Outra ação")


@pytest.mark.asyncio
async def test_execute_roll_then_narrate():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Test", attributes={"Ag": 35}, wounds_max=10, fate_max=2)
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            turn_phase="awaiting_roll",
            pending_test={
                "payload": {"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0},
                "setup_narrative": "Você tenta.",
                "all_payloads": [{"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0}],
            },
        )
        db.add(session)
        await db.commit()

        roll_result = await gm.execute_roll(db, session.id)
        assert roll_result.roll_results
        assert roll_result.roll_results[0]["roll"] is not None

        await db.refresh(session)
        assert session.turn_phase == "awaiting_narrate"

        with patch.object(gm.llm, "complete", new_callable=AsyncMock, return_value="Você consegue passar."):
            narrated = await gm.narrate_roll(db, session.id)

        assert "consegue" in narrated.narrative
        await db.refresh(session)
        assert session.turn_phase == "normal"
        assert session.pending_test is None


@pytest.mark.asyncio
async def test_estado_combate_inicia_combate():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Magnus", attributes={"Ag": 40}, wounds_max=12, fate_max=2)
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        from app.llm.signals import ParsedSignal

        result = __import__("app.services.gm_orchestrator", fromlist=["TurnResult"]).TurnResult()
        signal = ParsedSignal(
            tag="ESTADO_COMBATE",
            payload={
                "acao": "iniciar",
                "inimigos": [{"nome": "Bandido", "agilidade": 28}],
            },
            raw="",
        )
        await gm._handle_signal(db, session, campaign, char, signal, result)
        await db.refresh(session)

        assert session.mode == SessionMode.COMBAT
        assert session.combat_state is not None
        assert session.combat_state["turn"] == 1
        assert len(session.combat_state["order"]) == 2


@pytest.mark.asyncio
async def test_advance_combat_turn():
    async with async_session() as db:
        char = PlayerCharacter(name="Magnus", attributes={"Ag": 40})
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        state = await enter_combat(
            db,
            session,
            [
                {"nome": "Magnus", "agility": 40},
                {"nome": "Bandido", "agility": 28},
            ],
        )
        assert state["turn"] == 1
        assert state["current_index"] == 0

        from app.services.session import advance_combat_turn

        next_state = await advance_combat_turn(db, session)
        assert next_state["turn"] == 2
        assert next_state["current_index"] == 1
