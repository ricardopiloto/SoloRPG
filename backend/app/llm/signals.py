import json
import re
from dataclasses import dataclass
from typing import Any

SIGNAL_PATTERN = re.compile(
    r"\[(TESTE|IMAGEM|FIM_SESSAO|NOVA_CAMPANHA|ACAO_SISTEMA|ESTADO_COMBATE|MUSICA)\]\s*"
    r"(\{[\s\S]*?\})\s*\[/\1\]",
    re.MULTILINE,
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


def parse_signals(text: str) -> ParsedResponse:
    signals: list[ParsedSignal] = []
    narrative = text
    for match in SIGNAL_PATTERN.finditer(text):
        tag = match.group(1)
        try:
            payload = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        signals.append(ParsedSignal(tag=tag, payload=payload, raw=match.group(0)))
        narrative = narrative.replace(match.group(0), "").strip()
    return ParsedResponse(narrative=narrative.strip(), signals=signals)


def has_pending_test(signals: list[ParsedSignal]) -> bool:
    return any(s.tag == "TESTE" for s in signals)
