import json
from unittest.mock import AsyncMock, patch

import pytest

from app.llm.adapter import DeepSeekAdapter


@pytest.mark.asyncio
async def test_deepseek_stream_yields_api_chunks():
    adapter = DeepSeekAdapter()

    async def fake_aiter_lines():
        yield 'data: {"choices":[{"delta":{"content":"Olá "}}]}'
        yield 'data: {"choices":[{"delta":{"content":"mundo"}}]}'
        yield "data: [DONE]"

    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.aiter_lines = fake_aiter_lines

    mock_stream_ctx = AsyncMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_client = AsyncMock()
    mock_client.stream = lambda *a, **k: mock_stream_ctx
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.llm.adapter.httpx.AsyncClient", return_value=mock_client):
        chunks = []
        async for chunk in adapter.stream("system", [{"role": "user", "content": "oi"}]):
            chunks.append(chunk)

    assert chunks == ["Olá ", "mundo"]
