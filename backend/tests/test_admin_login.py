import pytest
from httpx import AsyncClient

from app.config import Settings
from app.services.admin_user import ADMIN_EMAIL, ADMIN_USERNAME, normalize_admin_login_email
from tests.conftest import admin_login


def test_normalize_admin_login_email_alias():
    assert normalize_admin_login_email("admin") == ADMIN_EMAIL
    assert normalize_admin_login_email("Admin") == ADMIN_EMAIL
    assert normalize_admin_login_email(ADMIN_EMAIL) == ADMIN_EMAIL


def test_startup_config_requires_admin_password():
    s = Settings(auth_mode="fixed_admin", admin_password="short")
    with pytest.raises(RuntimeError, match="ADMIN_PASSWORD"):
        s.validate_startup_config()


def test_production_config_rejects_default_jwt():
    s = Settings(
        app_env="production",
        jwt_secret="change-me-in-production",
        auth_mode="fixed_admin",
        admin_password="secure-admin-pass",
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        s.validate_startup_config()


def test_production_fixed_admin_does_not_require_smtp():
    s = Settings(
        app_env="production",
        jwt_secret="a-secure-random-secret-with-enough-length",
        email_provider="mock",
        auth_mode="fixed_admin",
        admin_password="secure-admin-pass",
    )
    s.validate_startup_config()


def test_production_multi_user_requires_smtp():
    s = Settings(
        app_env="production",
        jwt_secret="a-secure-random-secret-with-enough-length",
        email_provider="mock",
        auth_mode="multi_user",
    )
    with pytest.raises(RuntimeError, match="EMAIL_PROVIDER"):
        s.validate_startup_config()


@pytest.mark.asyncio
async def test_auth_config_fixed_admin(client: AsyncClient):
    res = await client.get("/api/auth/config")
    assert res.status_code == 200
    data = res.json()
    assert data["auth_mode"] == "fixed_admin"
    assert data["login_username"] == ADMIN_USERNAME
    assert data["registration_enabled"] is False


@pytest.mark.asyncio
async def test_admin_login(client: AsyncClient):
    for email in (ADMIN_USERNAME, ADMIN_EMAIL):
        res = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "test-admin-pass"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["access_token"]
        assert data["user"]["email"] == ADMIN_EMAIL


@pytest.mark.asyncio
async def test_admin_wrong_password(client: AsyncClient):
    res = await client.post(
        "/api/auth/login",
        json={"email": "admin", "password": "wrong-password"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_has_starter(client: AsyncClient):
    headers = await admin_login(client)
    chars = await client.get("/api/characters", headers=headers)
    assert chars.status_code == 200
    assert len(chars.json()) >= 1


@pytest.mark.asyncio
async def test_register_returns_404_in_fixed_admin(client: AsyncClient):
    res = await client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "password1", "password_confirm": "password1"},
    )
    assert res.status_code == 404
