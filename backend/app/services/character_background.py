"""Generate character background prose via LLM (non-GM prompt)."""

from __future__ import annotations

import json
from typing import Any

from app.config import settings
from app.llm.adapter import get_llm_adapter
from app.llm.prompts import load_character_background_prompt


def _build_user_message(payload: dict[str, Any]) -> str:
    return json.dumps(
        {
            "nome": payload.get("name"),
            "especie": payload.get("species", "Humano"),
            "carreira": payload.get("career"),
            "talentos": payload.get("talents") or [],
            "pericias": payload.get("skills_summary"),
            "pertences": payload.get("trappings") or [],
            "dicas_jogador": payload.get("hints"),
        },
        ensure_ascii=False,
        indent=2,
    )


def _mock_background(payload: dict[str, Any]) -> str:
    name = payload.get("name", "O personagem")
    career = payload.get("career", "aventureiro")
    hints = payload.get("hints")
    extra = f" {hints.strip()}" if hints else ""
    return (
        f"{name} cresceu nas estradas do Reikland e encontrou refúgio na carreira de {career}, "
        f"onde aprendeu que sobrevivência custa mais do que ouro.{extra} "
        "Cicatrizes visíveis e invisíveis marcam quem confiou nas pessoas erradas — "
        "mas ainda há algo pelo qual valha a pena lutar nas sombras do Império."
    )


async def generate_background(payload: dict[str, Any]) -> str:
    name = (payload.get("name") or "").strip()
    career = (payload.get("career") or "").strip()
    if not name or not career:
        raise ValueError("Nome e carreira são obrigatórios para gerar background")

    if settings.llm_provider.lower() == "mock":
        return _mock_background(payload)

    system = load_character_background_prompt()
    user = _build_user_message(payload)
    llm = get_llm_adapter()
    text = await llm.complete(system, [{"role": "user", "content": user}])
    return text.strip()
