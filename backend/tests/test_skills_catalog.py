import os

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from app.rules.skills import SKILL_CATALOG, list_skills


def test_intuicao_in_skill_catalog():
    assert "Intuição" in SKILL_CATALOG
    assert SKILL_CATALOG["Intuição"] == "I"


def test_list_skills_includes_intuicao():
    skills = list_skills()
    intuicao = next(s for s in skills if s["name"] == "Intuição")
    assert intuicao["linked_attribute"] == "I"
