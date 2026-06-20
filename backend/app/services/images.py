import asyncio
import hashlib
import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import async_session
from app.db.models import Campaign, ImageJob, MapRegion, PlayerCharacter
from app.services.cloudflare_workers_ai import (
    CloudflareWorkersAIClient,
)

logger = logging.getLogger(__name__)

GENERATED_DIR = Path(__file__).resolve().parent.parent.parent / "generated_images"

PLACEHOLDER_BASE = "https://placehold.co/1024x576/1a1510/C9973A?text="

SCENE_PLACEHOLDERS = {
    "cena": "Cena+WFRP",
    "personagem": "Personagem",
    "mapa": "Mapa",
    "item": "Item",
}


def placeholder_url(image_type: str) -> str:
    return PLACEHOLDER_BASE + SCENE_PLACEHOLDERS.get(image_type, "WFRP")


def build_cache_key(image_type: str, description: str) -> str:
    return hashlib.sha256(f"{image_type}:{description[:200]}".encode()).hexdigest()[:32]


def image_file_path(job_id: UUID) -> Path:
    return GENERATED_DIR / f"{job_id}.jpg"


def image_file_url(job_id: UUID) -> str:
    base = settings.api_base_url.rstrip("/")
    return f"{base}/api/images/{job_id}/file"


def save_image_file(job_id: UUID, data: bytes) -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = image_file_path(job_id)
    path.write_bytes(data)
    return path


async def queue_image(
    db: AsyncSession,
    campaign_id: UUID,
    session_id: UUID | None,
    image_type: str,
    description: str,
    priority: str = "normal",
) -> ImageJob:
    cache_key = build_cache_key(image_type, description)

    cached = await db.scalar(
        select(ImageJob).where(
            ImageJob.campaign_id == campaign_id,
            ImageJob.cache_key == cache_key,
            ImageJob.status == "completed",
        )
    )
    if cached:
        return cached

    job = ImageJob(
        campaign_id=campaign_id,
        session_id=session_id,
        image_type=image_type,
        description=description,
        priority=priority,
        status="pending",
        image_url=None,
        cache_key=cache_key,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    schedule_image_job(job.id)
    return job


def schedule_image_job(job_id: UUID) -> None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_run_image_job(job_id))
    except RuntimeError:
        asyncio.run(_run_image_job(job_id))


async def _run_image_job(job_id: UUID) -> None:
    async with async_session() as db:
        try:
            await process_image_job(db, job_id)
        except Exception:
            logger.exception("Unhandled error processing image job %s", job_id)


async def process_image_job(db: AsyncSession, job_id: UUID) -> None:
    job = await db.scalar(select(ImageJob).where(ImageJob.id == job_id))
    if not job or job.status in ("completed", "failed"):
        return

    job.status = "processing"
    await db.commit()

    client = CloudflareWorkersAIClient()

    if not client.enabled:
        job.status = "failed"
        job.image_url = None
        await db.commit()
        return

    try:
        image_bytes = await client.generate_image(job.description, job.image_type)
        save_image_file(job_id, image_bytes)
        job.image_url = image_file_url(job_id)
        job.status = "completed"
    except Exception as exc:
        logger.warning("Image job %s failed (%s): %s", job_id, type(exc).__name__, exc)
        job.status = "failed"
        job.image_url = None

    await db.commit()
    await _link_job_assets(db, job)


async def _link_job_assets(db: AsyncSession, job: ImageJob) -> None:
    if job.status != "completed" or not job.image_url:
        return

    if job.image_type == "mapa":
        region = await db.scalar(
            select(MapRegion)
            .where(
                MapRegion.campaign_id == job.campaign_id,
                MapRegion.name == job.description[:120],
            )
            .order_by(MapRegion.id.desc())
        )
        if region:
            region.image_url = job.image_url

    elif job.image_type == "item":
        campaign = await db.scalar(select(Campaign).where(Campaign.id == job.campaign_id))
        if not campaign:
            return
        character = await db.scalar(
            select(PlayerCharacter).where(PlayerCharacter.id == campaign.character_id)
        )
        if not character or not character.trappings:
            return
        desc_lower = job.description.lower()
        trappings = []
        updated = False
        for trapping in character.trappings:
            entry = dict(trapping)
            name = entry.get("name", "")
            if name.lower() in desc_lower or desc_lower in name.lower():
                entry["image_url"] = job.image_url
                updated = True
            trappings.append(entry)
        if updated:
            character.trappings = trappings

    await db.commit()


async def get_image_job(db: AsyncSession, job_id: UUID) -> ImageJob | None:
    return await db.scalar(select(ImageJob).where(ImageJob.id == job_id))
