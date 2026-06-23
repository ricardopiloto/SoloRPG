"""WFRP4e species definitions for character creation (MVP: Human/Reikland)."""

from typing import Any

ATTRIBUTE_NAMES = ["WS", "BS", "S", "T", "I", "Ag", "Dex", "Int", "WP", "Fel"]

SPECIES: dict[str, dict[str, Any]] = {
    "human": {
        "id": "human",
        "name": "Humano",
        "subspecies": {"reikland": "Reikland"},
        "characteristic_bonus": 20,
        "characteristic_formula": "2d10+20",
        "fate_base": 0,
        "extra_pool": 2,
        "xp_if_rolled": 20,
        "movement": 4,
        "skills": [
            "Charme",
            "Conhecimento (Reikland)",
            "Intimidação",
            "Liderança",
            "Percepção",
            "Atletismo",
            "Furtividade",
            "Navegação",
            "Orientação",
            "Vontade",
        ],
        "random_talents": ["Sortudo", "Robusto", "Olhos de Águia", "Corredor", "Discreto", "Forte"],
    },
}


def get_species(species_id: str) -> dict[str, Any] | None:
    return SPECIES.get(species_id)


def list_species() -> list[dict[str, Any]]:
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "subspecies": list(s.get("subspecies", {}).values()),
            "xp_if_rolled": s["xp_if_rolled"],
            "extra_pool": s["extra_pool"],
            "skills": s["skills"],
        }
        for s in SPECIES.values()
    ]


def creation_options() -> dict[str, Any]:
    return {
        "species": list_species(),
        "xp_awards": {
            "species_roll": 20,
            "career_first_roll": 50,
            "career_second_roll": 25,
            "attributes_first_roll": 50,
            "attributes_swap": 25,
            "attribute_advance_cost": 10,
        },
        "attribute_rules": {
            "roll_formula": "2d10+20",
            "allocate_pool": 100,
            "allocate_min": 4,
            "allocate_max": 18,
            "max_advances": 5,
        },
        "skill_rules": {
            "species_max_plus_3": 3,
            "species_max_plus_5": 3,
            "species_advance_options": [0, 3, 5],
            "career_point_pool": 40,
            "career_skill_max": 10,
        },
        "attribute_names": ATTRIBUTE_NAMES,
    }
