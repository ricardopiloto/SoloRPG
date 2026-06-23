from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_verified_user, require_multi_user_auth
from app.config import settings
from app.db.database import get_db
from app.db.models import User
from app.schemas.api import (
    AuthConfigOut,
    AuthTokenOut,
    CharacterOut,
    LoginRequest,
    RegisterOut,
    RegisterRequest,
    ResendVerificationRequest,
    UserOut,
    VerifyEmailRequest,
)
from app.services.admin_user import ADMIN_USERNAME
from app.services.auth import (
    authenticate_user,
    create_user,
    issue_verification_code,
    verify_email_code,
)
from app.services.jwt_tokens import create_access_token
from app.services.starter_character import generate_random_starter_character

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        email_verified=user.email_verified_at is not None,
        created_at=user.created_at,
    )


def _auth_response(user: User, starter: CharacterOut | None = None) -> AuthTokenOut:
    token = create_access_token(user_id=user.id, email=user.email)
    return AuthTokenOut(
        access_token=token,
        user=_user_out(user),
        starter_character=starter,
    )


@router.get("/config", response_model=AuthConfigOut)
async def auth_config():
    return AuthConfigOut(
        auth_mode=settings.auth_mode.strip().lower(),
        login_username=ADMIN_USERNAME,
        registration_enabled=settings.is_multi_user,
    )


@router.post("/register", response_model=RegisterOut, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_multi_user_auth),
):
    try:
        user = await create_user(db, body.email, body.password)
        await issue_verification_code(db, user)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return RegisterOut(user_id=user.id, email=user.email)


@router.post("/verify-email", response_model=AuthTokenOut)
async def verify_email(
    body: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_multi_user_auth),
):
    try:
        user = await verify_email_code(db, body.email, body.code)
        starter = await generate_random_starter_character(db, user.id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return _auth_response(user, CharacterOut.model_validate(starter))


@router.post("/resend-verification")
async def resend_verification(
    body: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_multi_user_auth),
):
    from app.services.auth import get_user_by_email

    user = await get_user_by_email(db, body.email)
    if not user:
        raise HTTPException(400, "E-mail não encontrado")
    try:
        await issue_verification_code(db, user, is_resend=True)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {"ok": True}


@router.post("/login", response_model=AuthTokenOut)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await authenticate_user(db, body.email, body.password)
    except ValueError as e:
        if str(e) == "verification_required":
            raise HTTPException(
                403,
                detail={"verification_required": True, "message": "Verifique seu e-mail antes de entrar"},
            ) from e
        raise HTTPException(401, "E-mail ou senha inválidos") from e
    return _auth_response(user)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_verified_user)):
    return _user_out(user)
