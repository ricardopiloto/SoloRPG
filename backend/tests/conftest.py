import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["EMAIL_PROVIDER"] = "mock"
os.environ["JWT_SECRET"] = "test-secret-key-for-pytest-min-32-chars"
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("AUTH_MODE", "fixed_admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-pass")

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.database import async_session, engine
from app.db.models import Base
from app.db.schema_patch import apply_schema_patches
from app.email.adapter import mock_sent_codes
from app.main import app
from app.services.admin_user import ensure_admin_user


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await apply_schema_patches(conn)
    from app.config import settings

    if settings.is_fixed_admin:
        async with async_session() as db:
            await ensure_admin_user(db)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def multi_user(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "auth_mode", "multi_user")


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def clear_mock_codes():
    mock_sent_codes.clear()
    yield
    mock_sent_codes.clear()


async def admin_login(client: AsyncClient, password: str | None = None) -> dict:
    pwd = password or os.environ["ADMIN_PASSWORD"]
    res = await client.post(
        "/api/auth/login",
        json={"email": "admin", "password": pwd},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def register_user(client: AsyncClient, email: str = "player@example.com", password: str = "secret123") -> dict:
    mock_sent_codes.clear()
    res = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "password_confirm": password},
    )
    assert res.status_code == 201, res.text
    return res.json()


async def verify_user(client: AsyncClient, email: str = "player@example.com") -> dict:
    code = mock_sent_codes[email]
    res = await client.post("/api/auth/verify-email", json={"email": email, "code": code})
    assert res.status_code == 200, res.text
    return res.json()


async def auth_headers(
    client: AsyncClient,
    email: str = "player@example.com",
    password: str = "secret123",
) -> dict:
    from app.config import settings

    if settings.is_multi_user:
        await register_user(client, email, password)
        data = await verify_user(client, email)
        token = data["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return await admin_login(client)


async def seed_user_character(db, email: str = "seed@example.com"):
    """Create verified user + character for service/API tests."""
    from datetime import datetime, timezone

    from app.db.models import CharacterStatus, PlayerCharacter, User
    from app.services.auth import hash_password
    from app.services.jwt_tokens import create_access_token

    user = User(
        email=email,
        password_hash=hash_password("secret123"),
        email_verified_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    char = PlayerCharacter(
        name="Hero",
        user_id=user.id,
        status=CharacterStatus.ALIVE,
        attributes={"Ag": 35},
    )
    db.add(char)
    await db.commit()
    await db.refresh(user)
    await db.refresh(char)
    token = create_access_token(user_id=user.id, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}
    return user, char, headers
