import json
import re
from dataclasses import dataclass
from typing import Any

SIGNAL_TAGS = (
    "TESTE",
    "IMAGEM",
    "FIM_SESSAO",
    "NOVA_CAMPANHA",
    "ACAO_SISTEMA",
    "ESTADO_COMBATE",
    "MUSICA",
)

SIGNAL_PATTERN = re.compile(
    r"\[(TESTE|IMAGEM|FIM_SESSAO|NOVA_CAMPANHA|ACAO_SISTEMA|ESTADO_COMBATE|MUSICA)\]\s*"
    r"(\{[\s\S]*?\})\s*\[/\1\]",
    re.MULTILINE,
)

# Typo-tolerant close tags for NOVA_CAMPANHA (e.g. [/NOVA_CAMAPANHA])
NOVA_CAMPANHA_LOOSE = re.compile(
    r"\[NOVA_CAMPANHA\]\s*(\{[\s\S]*?\})\s*\[/NOVA_CAM[AÁP]*NHA\]",
    re.IGNORECASE | re.MULTILINE,
)

# Remove remaining signal blocks with JSON + any closing tag
LOOSE_SIGNAL_BLOCK = re.compile(
    r"\[(TESTE|IMAGEM|FIM_SESSAO|NOVA_CAMPANHA|ACAO_SISTEMA|ESTADO_COMBATE|MUSICA)\]\s*"
    r"(\{[\s\S]*?\})\s*\[/[^\]]+\]",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass
class ParsedSignal:
    tag: str
    payload: dict[str, Any]
    raw: str


@dataclass
class ParsedResponse:
    narrative: str
    signals: list[ParsedSignal]


def _try_parse_payload(raw_json: str) -> dict[str, Any] | None:
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return None


def strip_signal_artifacts(text: str) -> str:
    """Remove signal blocks from player-visible narrative (safety net after parse)."""
    result = SIGNAL_PATTERN.sub("", text)
    result = NOVA_CAMPANHA_LOOSE.sub("", result)
    result = LOOSE_SIGNAL_BLOCK.sub("", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def parse_signals(text: str) -> ParsedResponse:
    signals: list[ParsedSignal] = []
    removed_blocks: list[str] = []

    for match in SIGNAL_PATTERN.finditer(text):
        payload = _try_parse_payload(match.group(2))
        if payload is None:
            continue
        raw = match.group(0)
        signals.append(ParsedSignal(tag=match.group(1), payload=payload, raw=raw))
        removed_blocks.append(raw)

    if not any(s.tag == "NOVA_CAMPANHA" for s in signals):
        for match in NOVA_CAMPANHA_LOOSE.finditer(text):
            payload = _try_parse_payload(match.group(1))
            if payload is None:
                continue
            raw = match.group(0)
            signals.append(ParsedSignal(tag="NOVA_CAMPANHA", payload=payload, raw=raw))
            removed_blocks.append(raw)
            break

    narrative = text
    for raw in removed_blocks:
        narrative = narrative.replace(raw, "", 1)
    narrative = strip_signal_artifacts(narrative)
    return ParsedResponse(narrative=narrative, signals=signals)


def has_pending_test(signals: list[ParsedSignal]) -> bool:
    return any(s.tag == "TESTE" for s in signals)
