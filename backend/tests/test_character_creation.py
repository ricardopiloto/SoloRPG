import os

import pytest

os.environ["DATABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "mock"

from app.rules.character_creation import (
    compute_fate_max,
    compute_wounds_max,
    creation_xp_awarded,
    draft_to_character_data,
    roll_all_characteristics,
    validate_draft,
)


def test_roll_characteristics_range():
    attrs = roll_all_characteristics()
    assert len(attrs) == 10
    for v in attrs.values():
        assert 22 <= v <= 40


def test_wounds_from_strength_toughness():
    assert compute_wounds_max({"S": 35, "T": 38}) == 6


def test_fate_human_extra_pool():
    assert compute_fate_max("human", 2) == 2


def test_creation_xp_roll_paths():
    assert creation_xp_awarded({"species_method": "roll", "attributes_method": "roll"}) == 70
    assert creation_xp_awarded({"species_method": "choose", "attributes_method": "roll", "attributes_swapped": True}) == 25


def test_validate_rejects_excess_career_skills():
    draft = {
        "species_id": "human",
        "career_id": "soldado",
        "career_skills": {s: 10 for s in ["Luta", "Atletismo", "Percepção", "Vontade", "Intimidação"]},
        "career_talent": "Resolução",
        "attribute_rolls": roll_all_characteristics(),
        "attributes_method": "roll",
        "name": "Test",
    }
    errors = validate_draft(draft, final=True)
    assert any(e["field"] == "career" for e in errors)


def test_draft_to_character_happy_path():
    career_skills = {
        "Luta": 8,
        "Atletismo": 6,
        "Percepção": 5,
        "Vontade": 5,
        "Intimidação": 4,
        "Orientação": 4,
        "Atirar (Armas de Fogo)": 4,
        "Charme": 4,
    }
    draft = {
        "species_id": "human",
        "species_method": "choose",
        "career_id": "soldado",
        "career_method": "choose",
        "attributes_method": "roll",
        "attribute_rolls": roll_all_characteristics(),
        "attribute_advances": {},
        "fate_allotted": 2,
        "species_skills": {"Charme": 3, "Percepção": 3, "Atletismo": 5},
        "career_skills": career_skills,
        "career_talent": "Resolução",
        "species_talents": ["Sortudo"],
        "name": "Helena Test",
        "background": "Ex-soldado",
    }
    errors = validate_draft(draft, final=True)
    assert errors == []
    data = draft_to_character_data(draft)
    assert data["name"] == "Helena Test"
    assert data["careers"][0]["name"] == "Soldado"
    assert data["wounds_max"] >= 1
    assert data["fate_max"] == 2
