import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, GameSession, ImageJob, PlayerCharacter
from app.llm.signals import ParsedSignal
from app.services.gm_orchestrator import GMOrchestrator, TurnResult
from app.services.images import process_image_job
from app.services.openrouter_images import (
    OpenRouterGenerationError,
    OpenRouterNotConfigured,
    is_quota_or_credit_error,
    probe_image_credits,
)
from app.services.session import start_session


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _seed_campaign(db):
    character = PlayerCharacter(name="Test Hero", attributes={"WS": 35})
    db.add(character)
    await db.flush()
    campaign = Campaign(character_id=character.id, status=CampaignStatus.ACTIVE)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    await db.refresh(character)
    return campaign, character


def test_is_quota_or_credit_error_classifies_quota_cases():
    assert is_quota_or_credit_error(OpenRouterNotConfigured("missing"))
    assert is_quota_or_credit_error(
        OpenRouterGenerationError("OpenRouter quota/rate limit (HTTP 429)"
    ))
    assert is_quota_or_credit_error(
        OpenRouterGenerationError("OpenRouter payment required / credits insufficient (HTTP 402)")
    )
    assert is_quota_or_credit_error(
        OpenRouterGenerationError("OpenRouter response missing image data: insufficient credits")
    )
    assert not is_quota_or_credit_error(OpenRouterGenerationError("OpenRouter HTTP 503"))
    assert not is_quota_or_credit_error(TimeoutError("timeout"))


@pytest.mark.asyncio
async def test_probe_ok_enables_images():
    mock_client = AsyncMock()
    mock_client.enabled = True
    mock_client.generate_image = AsyncMock(return_value=b"jpeg")

    assert await probe_image_credits(mock_client) is True
    mock_client.generate_image.assert_awaited_once()


@pytest.mark.asyncio
async def test_probe_failure_disables_when_credentials_missing():
    mock_client = AsyncMock()
    mock_client.enabled = False

    assert await probe_image_credits(mock_client) is False
    mock_client.generate_image.assert_not_called()


@pytest.mark.asyncio
async def test_start_session_probe_ok_sets_images_enabled():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        with patch(
            "app.services.session.probe_image_credits",
            new_callable=AsyncMock,
            return_value=True,
        ) as probe:
            session = await start_session(db, campaign.id)

        probe.assert_awaited_once()
        assert session.images_enabled is True


@pytest.mark.asyncio
async def test_start_session_probe_fail_keeps_images_disabled():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        with patch(
            "app.services.session.probe_image_credits",
            new_callable=AsyncMock,
            return_value=False,
        ):
            session = await start_session(db, campaign.id)

        assert session.images_enabled is False


@pytest.mark.asyncio
async def test_resumed_paused_session_does_not_reprobe():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        paused = GameSession(
            campaign_id=campaign.id,
            is_active=True,
            images_enabled=False,
            paused_at=datetime.now(timezone.utc),
        )
        db.add(paused)
        await db.commit()

        with patch(
            "app.services.session.probe_image_credits",
            new_callable=AsyncMock,
        ) as probe:
            session = await start_session(db, campaign.id)

        probe.assert_not_called()
        assert session.id == paused.id
        assert session.images_enabled is False


@pytest.mark.asyncio
async def test_handle_signal_ignores_imagem_when_disabled():
    gm = GMOrchestrator()
    async with async_session() as db:
        campaign, character = await _seed_campaign(db)
        session = GameSession(campaign_id=campaign.id, is_active=True, images_enabled=False)
        db.add(session)
        await db.commit()

        result = TurnResult()
        signal = ParsedSignal(
            tag="IMAGEM",
            payload={"tipo": "cena", "descricao": "Uma taverna"},
            raw="",
        )

        with patch("app.services.images.queue_image", new_callable=AsyncMock) as queue:
            await gm._handle_signal(db, session, campaign, character, signal, result)

        queue.assert_not_called()
        assert result.images == []


@pytest.mark.asyncio
async def test_quota_mid_session_disables_session_images():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        session = GameSession(campaign_id=campaign.id, is_active=True, images_enabled=True)
        db.add(session)
        await db.flush()
        job = ImageJob(
            campaign_id=campaign.id,
            session_id=session.id,
            image_type="cena",
            description="Cena",
            status="pending",
            cache_key="quota-test",
        )
        db.add(job)
        await db.commit()
        await db.refresh(session)

        mock_client = AsyncMock()
        mock_client.enabled = True
        mock_client.generate_image = AsyncMock(
            side_effect=OpenRouterGenerationError("OpenRouter quota/rate limit (HTTP 429)")
        )

        with patch("app.services.images.OpenRouterImagesClient", return_value=mock_client):
            await process_image_job(db, job.id)

        await db.refresh(session)
        assert session.images_enabled is False


@pytest.mark.asyncio
async def test_transient_error_does_not_disable_session_images():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        session = GameSession(campaign_id=campaign.id, is_active=True, images_enabled=True)
        db.add(session)
        await db.flush()
        job = ImageJob(
            campaign_id=campaign.id,
            session_id=session.id,
            image_type="cena",
            description="Cena",
            status="pending",
            cache_key="transient-test",
        )
        db.add(job)
        await db.commit()
        await db.refresh(session)

        mock_client = AsyncMock()
        mock_client.enabled = True
        mock_client.generate_image = AsyncMock(
            side_effect=OpenRouterGenerationError("OpenRouter HTTP 503")
        )

        with patch("app.services.images.OpenRouterImagesClient", return_value=mock_client):
            await process_image_job(db, job.id)

        await db.refresh(session)
        assert session.images_enabled is True
