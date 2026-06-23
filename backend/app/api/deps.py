import secrets
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Campaign, GameSession, PlayerCharacter, User
from app.services.jwt_tokens import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def require_multi_user_auth() -> None:
    from app.config import settings

    if not settings.is_multi_user:
        raise HTTPException(404, "Not available in phase 1")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Autenticação necessária")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(401, "Token inválido ou expirado") from None

    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(401, "Usuário não encontrado")
    return user


async def get_verified_user(user: User = Depends(get_current_user)) -> User:
    if user.email_verified_at is None:
        raise HTTPException(403, detail={"verification_required": True, "message": "E-mail não verificado"})
    return user


def require_custom_chargen_enabled() -> None:
    from app.config import settings

    if not settings.enable_custom_chargen:
        raise HTTPException(403, "Criação customizada indisponível nesta fase.")
