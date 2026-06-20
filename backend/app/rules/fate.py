from dataclasses import dataclass


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
    bonus: int = 0


def spend_fate_point(fate_current: int, wounds_max: int) -> FateSpendResult:
    if fate_current <= 0:
        return FateSpendResult(False, 0, 0, "Sem Pontos de Destino disponíveis.")
    return FateSpendResult(
        True,
        1,
        fate_current - 1,
        "Ponto de Destino gasto — personagem sobrevive com 1 wound.",
    )


def spend_fortune_point(fortune_current: int, effect: str = "bonus_teste") -> FortuneSpendResult:
    if fortune_current <= 0:
        return FortuneSpendResult(False, 0, "Sem Pontos de Fortuna disponíveis.")
    if effect == "reroll":
        return FortuneSpendResult(
            True,
            fortune_current - 1,
            "Ponto de Fortuna gasto — rolagem refeita.",
        )
    return FortuneSpendResult(
        True,
        fortune_current - 1,
        "Ponto de Fortuna gasto — +10 no teste.",
        bonus=10,
    )
