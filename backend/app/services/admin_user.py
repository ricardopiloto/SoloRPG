import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.auth import create_user, get_user_by_email, hash_password, normalize_email
from app.services.starter_character import generate_random_starter_character, user_has_starter

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "admin@wfrp-solo.local"
ADMIN_USERNAME = "admin"


def normalize_admin_login_email(email: str) -> str:
    normalized = normalize_email(email)
    if normalized == ADMIN_USERNAME:
        return ADMIN_EMAIL
    return normalized


async def ensure_admin_user(db: AsyncSession) -> None:
    if not settings.is_fixed_admin:
        return
    if not settings.admin_password:
        return

    user = await get_user_by_email(db, ADMIN_EMAIL)
    now = datetime.now(timezone.utc)

    if not user:
        user = await create_user(db, ADMIN_EMAIL, settings.admin_password)
        user.email_verified_at = now
        await db.commit()
        await db.refresh(user)
        logger.info("Admin user created (%s)", ADMIN_EMAIL)
    else:
        user.password_hash = hash_password(settings.admin_password)
        if user.email_verified_at is None:
            user.email_verified_at = now
        await db.commit()
        await db.refresh(user)

    if not await user_has_starter(db, user.id):
        await generate_random_starter_character(db, user.id)
        logger.info("Admin starter character created")
