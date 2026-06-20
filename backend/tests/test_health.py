import os

os.environ["DATABASE_PROFILE"] = "sqlite-dev"
os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_includes_database_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["database_profile"] == "sqlite-dev"
    assert data["database_ok"] is True
    assert "llm_provider" in data
