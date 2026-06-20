from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
import json
from typing import Any

import httpx

from app.config import settings


class LLMAdapter(ABC):
    @abstractmethod
    async def complete(self, system: str, messages: list[dict[str, str]]) -> str:
        pass

    @abstractmethod
    async def stream(self, system: str, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        pass


class MockLLMAdapter(LLMAdapter):
    async def complete(self, system: str, messages: list[dict[str, str]]) -> str:
        user_msg = messages[-1]["content"] if messages else ""
        return _mock_response_for_user(user_msg)

    async def stream(self, system: str, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        text = await self.complete(system, messages)
        for word in text.split(" "):
            yield word + " "


def _player_action(user_msg: str) -> str:
    marker = "ação do jogador:"
    lower = user_msg.lower()
    idx = lower.rfind(marker)
    if idx == -1:
        return user_msg.strip()
    return user_msg[idx + len(marker) :].strip()


def _mock_response_for_user(user_msg: str) -> str:
    lower = user_msg.lower()
    action = _player_action(user_msg).lower()

    if "resultado do teste" in lower or "rolou" in lower:
        return (
            "Você completa a ação com esforço visível. O mundo reage — "
            "passos ecoam ao longe.\n\nO que você faz?"
        )
    if action == "e2e-roll":
        return _mock_e2e_roll()
    if action == "e2e-end":
        return _mock_e2e_end()
    if action in {"início da sessão.", "inicio da sessao."} or "início da sessão" in action:
        return _mock_first_session()
    return (
        "A taverna cheira a fumaça e cerveja barata. Olhares desconfiados "
        "acompanham cada movimento seu.\n\nO que você faz?"
    )


class AnthropicAdapter(LLMAdapter):
    async def complete(self, system: str, messages: list[dict[str, str]]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "max_tokens": 4096,
                    "system": system,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

    async def stream(self, system: str, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        text = await self.complete(system, messages)
        for word in text.split(" "):
            yield word + " "


class DeepSeekAdapter(LLMAdapter):
    def _chat_url(self) -> str:
        base = settings.deepseek_base_url.rstrip("/")
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def _payload(self, system: str, messages: list[dict[str, str]], stream: bool) -> dict[str, Any]:
        return {
            "model": settings.llm_model or "deepseek-chat",
            "messages": [{"role": "system", "content": system}, *messages],
            "max_tokens": 4096,
            "stream": stream,
        }

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

    async def complete(self, system: str, messages: list[dict[str, str]]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                self._chat_url(),
                headers=self._headers(),
                json=self._payload(system, messages, stream=False),
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def stream(self, system: str, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                self._chat_url(),
                headers=self._headers(),
                json=self._payload(system, messages, stream=True),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                    if delta:
                        yield delta


def get_llm_adapter() -> LLMAdapter:
    provider = settings.llm_provider.lower()
    if provider == "anthropic":
        return AnthropicAdapter()
    if provider == "deepseek":
        return DeepSeekAdapter()
    return MockLLMAdapter()


def _mock_first_session() -> str:
    return """[NOVA_CAMPANHA]
{
  "tom": "sombrio/político",
  "localizacao_abertura": "Porto de Marienburg, Distrito dos Estivadores",
  "gancho_inicial": "Uma carta anônima no bolso do personagem ao acordar",
  "objetivo_secreto": "Desmantelar uma célula do culto infiltrada no Conselho de Mercadores",
  "antagonista": "Konsul Aldric Voss — comerciante respeitado, cultista devoto",
  "npcs_iniciais": [
    {"nome": "Greta", "papel": "taberneira", "segredo": "informante involuntária"},
    {"nome": "Sergeant Hoffman", "papel": "guarda corrupto", "relacao": "hostil"}
  ],
  "duracao_estimada_sessao_minutos": 45
}
[/NOVA_CAMPANHA]

Você acorda em um quarto úmido acima de uma taverna. A carta anônima ainda está no bolso — tinta fresca, selo quebrado. Passos pesados sobem a escada.

O que você faz?"""


def _mock_e2e_roll() -> str:
    return (
        'O corredor estreito exige cautela.\n[TESTE]{"tipo":"teste_atributo","atributo":"Ag",'
        '"pericia":"Atletismo","modificador":0}[/TESTE]'
    )


def _mock_e2e_end() -> str:
    return """A noite cai sobre Marienburg.

[FIM_SESSAO]
{
  "resumo_jogador": "Você sobreviveu ao primeiro dia na cidade. A carta anônima ainda guarda segredos.",
  "resumo_sistema": {
    "eventos_principais": ["Chegou ao porto"],
    "xp_sugerido": 45,
    "karma_delta": 0
  }
}
[/FIM_SESSAO]"""
