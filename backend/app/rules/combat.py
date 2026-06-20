from dataclasses import dataclass

from app.rules.dice import roll_d100
from app.rules.tests import TestResult, resolve_test


RANGE_MODIFIERS = {
    "curto": 0,
    "medio": -10,
    "longo": -20,
    "extremo": -30,
}


@dataclass
class AttackResult:
    test: TestResult
    hit: bool
    damage: int
    critical: bool
    attacker: str
    target: str
    weapon: str

    def to_llm_text(self) -> str:
        if not self.hit:
            return (
                f"Ataque de {self.attacker} contra {self.target} com {self.weapon}: "
                f"rolou {self.test.roll}, alvo {self.test.target} — ERROU."
            )
        crit = " CRÍTICO!" if self.critical else ""
        return (
            f"Ataque de {self.attacker} contra {self.target} com {self.weapon}: "
            f"rolou {self.test.roll}, alvo {self.test.target} — ACERTO{crit}. "
            f"Dano: {self.damage}."
        )


def resolve_melee_attack(
    ws: int,
    strength: int,
    weapon_bonus: int,
    modifier: int,
    damage_reduction: int,
    attacker: str,
    target: str,
    weapon: str,
    roll: int | None = None,
) -> AttackResult:
    test = resolve_test(ws + weapon_bonus, modifier=modifier, roll=roll)
    hit = test.success
    damage = 0
    critical = False
    if hit:
        damage = max(0, strength + test.levels - damage_reduction)
        critical = test.roll <= 5 or damage >= 10
    return AttackResult(test, hit, damage, critical, attacker, target, weapon)


def resolve_ranged_attack(
    bs: int,
    modifier: int,
    range_key: str,
    strength: int,
    damage_reduction: int,
    attacker: str,
    target: str,
    weapon: str,
    roll: int | None = None,
) -> AttackResult:
    range_mod = RANGE_MODIFIERS.get(range_key, -10)
    test = resolve_test(bs, modifier=modifier + range_mod, roll=roll)
    hit = test.success
    damage = 0
    critical = False
    if hit:
        damage = max(0, strength + test.levels - damage_reduction)
        critical = test.roll <= 5
    return AttackResult(test, hit, damage, critical, attacker, target, weapon)


def roll_initiative(agility: int) -> int:
    from app.rules.dice import roll_d10

    return agility + roll_d10()
