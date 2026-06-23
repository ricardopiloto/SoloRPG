import logging
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EmailVerificationCode, User
from app.email.adapter import get_email_adapter

logger = logging.getLogger(__name__)

pwd_context = None  # legacy placeholder removed — use bcrypt directly


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def hash_code(code: str) -> str:
    return bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_code(code: str, code_hash: str) -> bool:
    return bcrypt.checkpw(code.encode("utf-8"), code_hash.encode("utf-8"))


def generate_verification_code() -> str:
    return str(secrets.randbelow(90000000) + 10000000)


CODE_EXPIRE_MINUTES = 15
MAX_CODE_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60

# In-memory resend tracking (MVP)
_last_resend_at: dict[str, datetime] = {}


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    normalized = normalize_email(email)
    return await db.scalar(select(User).where(User.email == normalized))


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    normalized = normalize_email(email)
    existing = await get_user_by_email(db, normalized)
    if existing:
        raise ValueError("E-mail já cadastrado")

    user = User(email=normalized, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def issue_verification_code(db: AsyncSession, user: User, *, is_resend: bool = False) -> str:
    if user.email_verified_at is not None:
        raise ValueError("Conta já verificada")

    normalized = user.email
    now = datetime.now(timezone.utc)
    if is_resend:
        last = _last_resend_at.get(normalized)
        if last and (now - last).total_seconds() < RESEND_COOLDOWN_SECONDS:
            raise ValueError("Aguarde um minuto antes de solicitar novo código")

    code = generate_verification_code()
    expires_at = now + timedelta(minutes=CODE_EXPIRE_MINUTES)

    pending = list(
        await db.scalars(
            select(EmailVerificationCode).where(
                EmailVerificationCode.user_id == user.id,
                EmailVerificationCode.used_at.is_(None),
            )
        )
    )
    for row in pending:
        row.used_at = now

    db.add(
        EmailVerificationCode(
            user_id=user.id,
            code_hash=hash_code(code),
            expires_at=expires_at,
        )
    )
    await db.commit()

    adapter = get_email_adapter()
    await adapter.send_verification_code(normalized, code)
    if is_resend:
        _last_resend_at[normalized] = now
    logger.info("Verification code issued for %s", normalized)
    return code


async def verify_email_code(db: AsyncSession, email: str, code: str) -> User:
    user = await get_user_by_email(db, email)
    if not user:
        raise ValueError("Código inválido")
    if user.email_verified_at is not None:
        raise ValueError("Conta já verificada")

    now = datetime.now(timezone.utc)
    record = await db.scalar(
        select(EmailVerificationCode)
        .where(
            EmailVerificationCode.user_id == user.id,
            EmailVerificationCode.used_at.is_(None),
        )
        .order_by(EmailVerificationCode.created_at.desc())
    )
    if not record:
        raise ValueError("Nenhum código pendente — solicite reenvio")

    expires = record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        raise ValueError("Código expirado — solicite um novo")

    if record.attempts >= MAX_CODE_ATTEMPTS:
        raise ValueError("Tentativas excedidas — solicite um novo código")

    if not verify_code(code.strip(), record.code_hash):
        record.attempts += 1
        await db.commit()
        raise ValueError("Código inválido")

    record.used_at = now
    user.email_verified_at = now
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    from app.config import settings
    from app.services.admin_user import ADMIN_EMAIL, normalize_admin_login_email

    if settings.is_fixed_admin:
        email = normalize_admin_login_email(email)
        if email != ADMIN_EMAIL:
            raise ValueError("E-mail ou senha inválidos")
        user = await get_user_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("E-mail ou senha inválidos")
        return user

    email = normalize_email(email)
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("E-mail ou senha inválidos")
    if user.email_verified_at is None:
        raise ValueError("verification_required")
    return user
