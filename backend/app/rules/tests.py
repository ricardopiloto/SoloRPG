from dataclasses import dataclass

from app.rules.dice import roll_d100


@dataclass
class TestResult:
    roll: int
    target: int
    success: bool
    levels: int
    description: str

    def to_llm_text(self, attribute: str) -> str:
        outcome = "SUCESSO" if self.success else "FALHA"
        n = abs(self.levels)
        level_word = "nível" if n == 1 else "níveis"
        return (
            f"Teste de {attribute}: rolou {self.roll}, alvo {self.target} — "
            f"{outcome} por {n} {level_word}. {self.description}"
        )


def compute_target(attribute: int, skill_advances: int = 0, modifier: int = 0) -> int:
    return max(1, min(100, attribute + skill_advances + modifier))


def resolve_test(
    attribute_value: int,
    skill_advances: int = 0,
    modifier: int = 0,
    description: str = "",
    roll: int | None = None,
) -> TestResult:
    target = compute_target(attribute_value, skill_advances, modifier)
    if roll is None:
        roll = roll_d100()
    else:
        roll = max(1, min(100, roll))
    success = roll <= target
    if success:
        levels = 1 + (target - roll) // 10
    else:
        levels = 1 + (roll - target) // 10
    return TestResult(
        roll=roll,
        target=target,
        success=success,
        levels=levels,
        description=description,
    )
