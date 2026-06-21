from dataclasses import dataclass
from typing import Literal

FateReason = Literal["avoid_wound", "avoid_death"]


@dataclass
class FateSpendResult:
    success: bool
    wounds_after: int
    fate_remaining: int
    message: str


@dataclass
class FortuneSpendResult:
    success: bool
    fortune_remaining: int
    message: str


def refresh_fortune_from_fate(fate_current: int) -> tuple[int, int]:
    """Return (fortune_current, fortune_max) tied to current Fate."""
    return fate_current, fate_current


def spend_fate_point(
    fate_current: int,
    wounds_current: int,
    wounds_max: int,
    reason: FateReason = "avoid_death",
) -> FateSpendResult:
    if fate_current <= 0:
        return FateSpendResult(False, wounds_current, 0, "Sem Pontos de Destino disponíveis.")
    if reason == "avoid_wound":
        return FateSpendResult(
            True,
            wounds_current,
            fate_current - 1,
            "Ponto de Destino gasto — ferimento evitado.",
        )
    return FateSpendResult(
        True,
        1,
        fate_current - 1,
        "Ponto de Destino gasto — personagem sobrevive com 1 wound.",
    )


def spend_fortune_point(fortune_current: int, effect: str = "reroll") -> FortuneSpendResult:
    if fortune_current <= 0:
        return FortuneSpendResult(False, 0, "Sem Pontos de Fortuna disponíveis.")
    if effect != "reroll":
        return FortuneSpendResult(False, fortune_current, "Fortuna só pode ser usada para re-rolar testes.")
    return FortuneSpendResult(
        True,
        fortune_current - 1,
        "Ponto de Fortuna gasto — rolagem refeita.",
    )
