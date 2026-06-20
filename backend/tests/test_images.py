import base64
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

os.environ.setdefault("CLOUDFLARE_ACCOUNT_ID", "test-account")
os.environ.setdefault("CLOUDFLARE_API_TOKEN", "test-token")
os.environ.setdefault("API_BASE_URL", "http://testserver")

from app.db.database import async_session, engine
from app.db.models import Base, Campaign, CampaignStatus, ImageJob, MapRegion, PlayerCharacter
from app.services.images import (
    GENERATED_DIR,
    build_cache_key,
    get_image_job,
    image_file_path,
    image_file_url,
    placeholder_url,
    process_image_job,
    queue_image,
    save_image_file,
)


@pytest.fixture(autouse=True)
async def setup_db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.images.GENERATED_DIR", tmp_path / "generated_images")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def noop_schedule(monkeypatch):
    monkeypatch.setattr("app.services.images.schedule_image_job", lambda _job_id: None)


async def _seed_campaign(db):
    character = PlayerCharacter(
        name="Test Hero",
        attributes={"WS": 35},
        trappings=[{"name": "Espada Longa", "encumbrance": 1}],
    )
    db.add(character)
    await db.flush()
    campaign = Campaign(character_id=character.id, status=CampaignStatus.ACTIVE)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    await db.refresh(character)
    return campaign, character


FAKE_JPEG = b"\xff\xd8\xff\xe0fake-jpeg-data"


@pytest.mark.asyncio
async def test_queue_image_creates_pending_job(noop_schedule):
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        job = await queue_image(db, campaign.id, None, "cena", "Uma taverna escura em Altdorf")
        assert job.status == "pending"
        assert job.image_url == placeholder_url("cena")
        assert job.cache_key == build_cache_key("cena", "Uma taverna escura em Altdorf")


@pytest.mark.asyncio
async def test_queue_image_uses_cache(noop_schedule):
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        first = await queue_image(db, campaign.id, None, "cena", "Mesma cena")
        first.status = "completed"
        first.image_url = "http://testserver/api/images/cached/file"
        await db.commit()

        second = await queue_image(db, campaign.id, None, "cena", "Mesma cena")
        assert second.id == first.id
        assert second.image_url == "http://testserver/api/images/cached/file"


@pytest.mark.asyncio
async def test_process_image_job_with_mock_cloudflare(tmp_path):
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        job = ImageJob(
            campaign_id=campaign.id,
            image_type="cena",
            description="Ponte sobre o Reik",
            status="pending",
            image_url=placeholder_url("cena"),
            cache_key=build_cache_key("cena", "Ponte sobre o Reik"),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        mock_client = AsyncMock()
        mock_client.enabled = True
        mock_client.generate_image = AsyncMock(return_value=FAKE_JPEG)

        with patch("app.services.images.CloudflareWorkersAIClient", return_value=mock_client):
            await process_image_job(db, job.id)

        updated = await get_image_job(db, job.id)
        assert updated.status == "completed"
        assert updated.image_url == image_file_url(job.id)
        assert image_file_path(job.id).read_bytes() == FAKE_JPEG


@pytest.mark.asyncio
async def test_process_image_job_updates_map_region():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        region_name = "Floresta Drakwald"
        region = MapRegion(
            campaign_id=campaign.id,
            name=region_name,
            description=region_name,
            image_url=placeholder_url("mapa"),
            revealed=True,
        )
        db.add(region)
        job = ImageJob(
            campaign_id=campaign.id,
            image_type="mapa",
            description=region_name,
            status="pending",
            image_url=placeholder_url("mapa"),
            cache_key=build_cache_key("mapa", region_name),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        mock_client = AsyncMock()
        mock_client.enabled = True
        mock_client.generate_image = AsyncMock(return_value=FAKE_JPEG)

        with patch("app.services.images.CloudflareWorkersAIClient", return_value=mock_client):
            await process_image_job(db, job.id)

        updated_region = await db.scalar(select(MapRegion).where(MapRegion.id == region.id))
        assert updated_region.image_url == image_file_url(job.id)


@pytest.mark.asyncio
async def test_process_image_job_links_item_to_inventory():
    async with async_session() as db:
        campaign, character = await _seed_campaign(db)
        job = ImageJob(
            campaign_id=campaign.id,
            image_type="item",
            description="Espada Longa",
            status="pending",
            image_url=placeholder_url("item"),
            cache_key=build_cache_key("item", "Espada Longa"),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        mock_client = AsyncMock()
        mock_client.enabled = True
        mock_client.generate_image = AsyncMock(return_value=FAKE_JPEG)

        with patch("app.services.images.CloudflareWorkersAIClient", return_value=mock_client):
            await process_image_job(db, job.id)

        await db.refresh(character)
        assert character.trappings[0]["image_url"] == image_file_url(job.id)


@pytest.mark.asyncio
async def test_process_image_job_fallback_without_credentials():
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        job = ImageJob(
            campaign_id=campaign.id,
            image_type="cena",
            description="Sem API",
            status="pending",
            image_url=placeholder_url("cena"),
            cache_key=build_cache_key("cena", "Sem API"),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        mock_client = AsyncMock()
        mock_client.enabled = False

        with patch("app.services.images.CloudflareWorkersAIClient", return_value=mock_client):
            await process_image_job(db, job.id)

        updated = await get_image_job(db, job.id)
        assert updated.status == "completed"
        assert updated.image_url == placeholder_url("cena")


@pytest.mark.asyncio
async def test_api_get_image_job(client, noop_schedule):
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        job = await queue_image(db, campaign.id, None, "cena", "Mercado imperial")
        response = await client.get(f"/api/images/{job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(job.id)
        assert data["status"] == "pending"
        assert data["image_type"] == "cena"
        assert data["placeholder_url"] == placeholder_url("cena")


@pytest.mark.asyncio
async def test_api_image_file_serves_jpeg(client, noop_schedule):
    async with async_session() as db:
        campaign, _ = await _seed_campaign(db)
        job = await queue_image(db, campaign.id, None, "cena", "Arquivo servido")
        save_image_file(job.id, FAKE_JPEG)

        response = await client.get(f"/api/images/{job.id}/file")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content == FAKE_JPEG


@pytest.mark.asyncio
async def test_cloudflare_client_decodes_base64():
    from app.services.cloudflare_workers_ai import CloudflareWorkersAIClient

    payload = base64.b64encode(FAKE_JPEG).decode()

    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json = lambda: {"success": True, "result": {"image": payload}}

    mock_http = AsyncMock()
    mock_http.post = AsyncMock(return_value=mock_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    client = CloudflareWorkersAIClient(
        account_id="acct",
        api_token="token",
        model="@cf/black-forest-labs/flux-1-schnell",
    )
    with patch("app.services.cloudflare_workers_ai.httpx.AsyncClient", return_value=mock_http):
        result = await client.generate_image("A grim tavern", "cena")
    assert result == FAKE_JPEG
