import os

os.environ["DATABASE_PROFILE"] = "sqlite-dev"
os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
