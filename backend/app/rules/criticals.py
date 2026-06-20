from dataclasses import dataclass

from app.rules.dice import roll_d10


CRITICAL_EFFECTS = [
    "Ferimento superficial — sangramento leve.",
    "Corte profundo — penalidade temporária.",
    "Fratura — membro afetado comprometido.",
    "Trauma interno — ferimento grave.",
    "Golpe letal — risco de morte imediata.",
]


@dataclass
class CriticalResult:
    roll: int
    severity: int
    effect: str
    lethal: bool


def resolve_critical() -> CriticalResult:
    roll = roll_d10()
    severity = min(5, max(1, roll // 2 + 1))
    effect = CRITICAL_EFFECTS[severity - 1]
    lethal = severity >= 5
    return CriticalResult(roll=roll, severity=severity, effect=effect, lethal=lethal)


def apply_wounds(current: int, damage: int) -> tuple[int, bool]:
    new_wounds = max(0, current - damage)
    at_zero = new_wounds == 0
    return new_wounds, at_zero
