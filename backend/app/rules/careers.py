from app.rules.skills import PROGRESSION_SKILL_NAMES, SKILL_CATALOG

XP_MIN = 30
XP_MAX = 100

SKILL_ADVANCE_COST = 5
TALENT_COST = 10
CAREER_ADVANCE_COST = 15

ATTRIBUTE_NAMES = ["WS", "BS", "S", "T", "I", "Ag", "Dex", "Int", "WP", "Fel"]

PROGRESSION_SKILLS = [
    {"name": name, "linked_attribute": SKILL_CATALOG[name]}
    for name in PROGRESSION_SKILL_NAMES
]

PROGRESSION_TALENTS = [
    "Resolução",
    "Robusto",
    "Olhos de Águia",
    "Corredor",
    "Discreto",
    "Sortudo",
    "Forte",
    "Ambidestro",
]


def validate_xp(xp_suggested: int) -> int:
    return max(XP_MIN, min(XP_MAX, xp_suggested))


def xp_available(total: int, spent: int) -> int:
    return max(0, total - spent)


def can_purchase_skill(advances: list, skill_name: str, xp_total: int, xp_spent: int) -> bool:
    return xp_available(xp_total, xp_spent) >= SKILL_ADVANCE_COST


def apply_skill_advance(skills: list, skill_name: str, linked_attribute: str) -> list:
    updated = list(skills)
    for skill in updated:
        if skill["name"] == skill_name:
            skill["advances"] = skill.get("advances", 0) + 1
            return updated
    updated.append({"name": skill_name, "advances": 1, "linked_attribute": linked_attribute})
    return updated
