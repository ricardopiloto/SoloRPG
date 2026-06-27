"""Tests for [MUSICA] scene_mood propagation."""

import pytest

from app.db.models import Campaign, CampaignStatus, GameSession, PlayerCharacter
from app.db.database import async_session
from app.llm.signals import ParsedSignal
from app.services.audio_moods import IN_GAME_MOODS
from app.services.gm_orchestrator import GMOrchestrator, TurnResult


@pytest.mark.parametrize(
    "mood",
    ["combate", "exploração", "investigação", "horror", "horror_caos", "social", "jornada", "tensão", "normal"],
)
def test_in_game_moods_whitelist_contains_expected_values(mood):
    assert mood in IN_GAME_MOODS


@pytest.mark.asyncio
@pytest.mark.parametrize("mood", ["combate", "horror", "horror_caos"])
async def test_handle_signal_musica_sets_scene_mood(mood):
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Test", attributes={"Ag": 30})
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        result = TurnResult()
        signal = ParsedSignal(
            tag="MUSICA",
            payload={"mood": mood, "descricao": "test"},
            raw="",
        )
        await gm._handle_signal(db, session, campaign, char, signal, result)
        assert result.scene_mood == mood


@pytest.mark.asyncio
async def test_handle_signal_musica_ignores_invalid_mood():
    gm = GMOrchestrator()
    async with async_session() as db:
        char = PlayerCharacter(name="Test", attributes={"Ag": 30})
        db.add(char)
        await db.flush()
        campaign = Campaign(character_id=char.id, status=CampaignStatus.ACTIVE)
        db.add(campaign)
        await db.flush()
        session = GameSession(campaign_id=campaign.id, is_active=True)
        db.add(session)
        await db.commit()

        result = TurnResult()
        signal = ParsedSignal(
            tag="MUSICA",
            payload={"mood": "tenso", "descricao": "invalid"},
            raw="",
        )
        await gm._handle_signal(db, session, campaign, char, signal, result)
        assert result.scene_mood is None
