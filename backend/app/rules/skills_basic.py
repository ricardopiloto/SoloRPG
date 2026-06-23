"""Basic WFRP skills granted at character creation (advances 0)."""

from app.rules.skills import SKILL_CATALOG

BASIC_SKILLS = sorted(SKILL_CATALOG.keys())


def basic_skill_entries() -> list[dict]:
    return [{"name": n, "advances": 0, "linked_attribute": SKILL_CATALOG[n]} for n in BASIC_SKILLS]
