"""WFRP4e character creation rules (Foundry chargen parity, Human MVP).

Reference: https://github.com/moo-man/WFRP4e-FoundryVTT/tree/master/src/apps/chargen
"""

from __future__ import annotations

import random
from typing import Any

from app.rules.careers_catalog import get_career, roll_human_career
from app.rules.dice import roll_d10
from app.rules.skills import SKILL_CATALOG
from app.rules.skills_basic import basic_skill_entries
from app.rules.species import ATTRIBUTE_NAMES, get_species

ATTR_ADVANCE_COST = 10
CAREER_SKILL_POOL = 40
CAREER_SKILL_MAX = 10
SPECIES_MAX_PLUS_3 = 3
SPECIES_MAX_PLUS_5 = 3
ALLOCATE_POOL = 100
ALLOCATE_MIN = 4
ALLOCATE_MAX = 18
MAX_ATTR_ADVANCES = 5


def roll_characteristic() -> int:
    return roll_d10() + roll_d10() + 20


def roll_all_characteristics() -> dict[str, int]:
    return {attr: roll_characteristic() for attr in ATTRIBUTE_NAMES}


def swap_characteristics(attrs: dict[str, int], a: str, b: str) -> dict[str, int]:
    out = dict(attrs)
    if a in out and b in out:
        out[a], out[b] = out[b], out[a]
    return out


def strength_bonus(s: int) -> int:
    return s // 10


def toughness_bonus(t: int) -> int:
    return t // 10


def compute_wounds_max(attributes: dict[str, int]) -> int:
    return max(1, strength_bonus(attributes.get("S", 30)) + toughness_bonus(attributes.get("T", 30)))


def compute_fate_max(species_id: str, fate_allotted: int) -> int:
    species = get_species(species_id) or get_species("human")
    base = species["fate_base"] if species else 0
    extra = species["extra_pool"] if species else 2
    allotted = min(max(0, fate_allotted), extra)
    return base + allotted


def creation_xp_awarded(draft: dict[str, Any]) -> int:
    xp = 0
    if draft.get("species_method") == "roll":
        xp += 20
    career_method = draft.get("career_method", "choose")
    roll_count = draft.get("career_roll_count", 0)
    if career_method == "roll":
        if roll_count == 1:
            xp += 50
        elif roll_count >= 2:
            xp += 25
    attr_method = draft.get("attributes_method", "roll")
    if attr_method == "roll":
        if draft.get("attributes_rerolled"):
            pass
        elif draft.get("attributes_swapped"):
            xp += 25
        else:
            xp += 50
    return xp


def xp_spent_on_creation(draft: dict[str, Any]) -> int:
    advances = draft.get("attribute_advances") or {}
    total_adv = sum(int(v) for v in advances.values())
    return total_adv * ATTR_ADVANCE_COST


def resolve_final_attributes(draft: dict[str, Any]) -> dict[str, int]:
    species = get_species(draft.get("species_id", "human")) or get_species("human")
    bonus = species["characteristic_bonus"]
    advances = draft.get("attribute_advances") or {}

    if draft.get("attributes_method") == "allocate":
        allocated = draft.get("attribute_allocated") or {}
        base = {attr: int(allocated.get(attr, 0)) + bonus for attr in ATTRIBUTE_NAMES}
    else:
        rolls = draft.get("attribute_rolls") or draft.get("attributes") or {}
        base = {attr: int(rolls.get(attr, 30)) for attr in ATTRIBUTE_NAMES}

    return {attr: base.get(attr, 30) + int(advances.get(attr, 0)) for attr in ATTRIBUTE_NAMES}


def roll_species_talent(species_id: str) -> str:
    species = get_species(species_id) or get_species("human")
    pool = species["random_talents"] if species else ["Sortudo"]
    return random.choice(pool)


def merge_skills(draft: dict[str, Any], career: dict[str, Any]) -> list[dict]:
    by_name: dict[str, dict] = {s["name"]: dict(s) for s in basic_skill_entries()}

    for skill, adv in (draft.get("species_skills") or {}).items():
        adv = int(adv)
        if adv <= 0:
            continue
        attr = SKILL_CATALOG.get(skill, "Int")
        if skill in by_name:
            by_name[skill]["advances"] = by_name[skill].get("advances", 0) + adv
        else:
            by_name[skill] = {"name": skill, "advances": adv, "linked_attribute": attr}

    for skill, adv in (draft.get("career_skills") or {}).items():
        adv = int(adv)
        if adv <= 0:
            continue
        attr = SKILL_CATALOG.get(skill, "Int")
        if skill in by_name:
            by_name[skill]["advances"] = by_name[skill].get("advances", 0) + adv
        else:
            by_name[skill] = {"name": skill, "advances": adv, "linked_attribute": attr}

    return sorted(by_name.values(), key=lambda s: s["name"])


def merge_talents(draft: dict[str, Any], career: dict[str, Any]) -> list[dict]:
    names: list[str] = []
    for t in draft.get("species_talents") or []:
        if t and t not in names:
            names.append(t)
    career_talent = draft.get("career_talent")
    if career_talent and career_talent not in names:
        names.append(career_talent)
    return [{"name": n} for n in names]


def validate_draft(draft: dict[str, Any], *, final: bool = False) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    species_id = draft.get("species_id", "human")
    if not get_species(species_id):
        errors.append({"step": "species", "field": "species_id", "message": "Espécie inválida"})

    career_id = draft.get("career_id")
    career = get_career(career_id) if career_id else None
    if final and not career:
        errors.append({"step": "career", "field": "career_id", "message": "Selecione uma carreira"})

    if draft.get("attributes_method") == "allocate":
        allocated = draft.get("attribute_allocated") or {}
        spent = sum(int(allocated.get(a, 0)) for a in ATTRIBUTE_NAMES)
        if spent > ALLOCATE_POOL:
            errors.append({"step": "attributes", "field": "allocate", "message": "Pool de pontos excedido"})
        for attr in ATTRIBUTE_NAMES:
            val = int(allocated.get(attr, 0))
            if val and (val < ALLOCATE_MIN or val > ALLOCATE_MAX):
                errors.append({"step": "attributes", "field": attr, "message": f"{attr} fora do intervalo 4–18"})
    elif final:
        attrs = draft.get("attribute_rolls") or draft.get("attributes")
        if not attrs or len(attrs) < 10:
            errors.append({"step": "attributes", "field": "rolls", "message": "Rolagem de atributos incompleta"})

    advances = draft.get("attribute_advances") or {}
    total_adv = sum(int(v) for v in advances.values())
    if total_adv > MAX_ATTR_ADVANCES:
        errors.append({"step": "attributes", "field": "advances", "message": "Máximo 5 avanços de atributo"})

    awarded = creation_xp_awarded(draft)
    spent = xp_spent_on_creation(draft)
    if spent > awarded:
        errors.append({"step": "attributes", "field": "xp", "message": "XP de criação insuficiente para avanços"})

    species = get_species(species_id) or get_species("human")
    if species:
        allowed = set(species["skills"])
        species_skills = draft.get("species_skills") or {}
        plus_3 = sum(1 for v in species_skills.values() if int(v) == 3)
        plus_5 = sum(1 for v in species_skills.values() if int(v) == 5)
        if plus_3 > SPECIES_MAX_PLUS_3:
            errors.append({"step": "skills", "field": "species", "message": "Máximo 3 perícias de espécie em +3"})
        if plus_5 > SPECIES_MAX_PLUS_5:
            errors.append({"step": "skills", "field": "species", "message": "Máximo 3 perícias de espécie em +5"})
        for skill, adv in species_skills.items():
            if int(adv) > 0 and skill not in allowed:
                errors.append({"step": "skills", "field": skill, "message": "Perícia não disponível para a espécie"})

    if career and final:
        career_skills = draft.get("career_skills") or {}
        total = sum(int(v) for v in career_skills.values())
        allowed_career = set(career["skills"])
        if total > CAREER_SKILL_POOL:
            errors.append({"step": "skills", "field": "career", "message": "Máximo 40 pontos em perícias de carreira"})
        for skill, adv in career_skills.items():
            adv = int(adv)
            if adv > CAREER_SKILL_MAX:
                errors.append({"step": "skills", "field": skill, "message": "Máximo 10 por perícia de carreira"})
            if adv > 0 and skill not in allowed_career:
                errors.append({"step": "skills", "field": skill, "message": "Perícia não pertence à carreira"})
        if not draft.get("career_talent"):
            errors.append({"step": "skills", "field": "career_talent", "message": "Escolha um talento de carreira"})
        elif draft.get("career_talent") not in career["talents"]:
            errors.append({"step": "skills", "field": "career_talent", "message": "Talento inválido para a carreira"})

    fate_allotted = draft.get("fate_allotted", 2)
    species_extra = species["extra_pool"] if species else 2
    if fate_allotted < 0 or fate_allotted > species_extra:
        errors.append({"step": "attributes", "field": "fate", "message": f"Destino alocado deve ser 0–{species_extra}"})

    if final and not (draft.get("name") or "").strip():
        errors.append({"step": "details", "field": "name", "message": "Nome obrigatório"})

    return errors


def compute_preview(draft: dict[str, Any]) -> dict[str, Any]:
    career = get_career(draft.get("career_id", "")) if draft.get("career_id") else None
    attributes = resolve_final_attributes(draft)
    fate_max = compute_fate_max(draft.get("species_id", "human"), draft.get("fate_allotted", 2))
    awarded = creation_xp_awarded(draft)
    spent = xp_spent_on_creation(draft)
    skills = merge_skills(draft, career) if career else basic_skill_entries()
    talents = merge_talents(draft, career) if career else []
    trappings = list(career["trappings"]) if career else []
    if career:
        trappings.append({"name": "Bolsa de moedas", "encumbrance": 1, "description": "50 coroas imperiais"})

    return {
        "attributes": attributes,
        "wounds_max": compute_wounds_max(attributes),
        "fate_max": fate_max,
        "fortune_max": fate_max,
        "xp_awarded": awarded,
        "xp_spent": spent,
        "xp_total": max(0, awarded - spent),
        "skills": skills,
        "talents": talents,
        "trappings": trappings,
        "career": {"id": career["id"], "name": career["name"]} if career else None,
    }


def draft_to_character_data(draft: dict[str, Any]) -> dict[str, Any]:
    errors = validate_draft(draft, final=True)
    if errors:
        raise ValueError(errors[0]["message"])
    preview = compute_preview(draft)
    career = get_career(draft["career_id"])
    return {
        "name": draft["name"].strip(),
        "background": (draft.get("background") or "").strip() or None,
        "attributes": preview["attributes"],
        "wounds_max": preview["wounds_max"],
        "fate_max": preview["fate_max"],
        "careers": [{"name": career["name"], "tier": 1, "advances_spent": 0}],
        "skills": preview["skills"],
        "talents": preview["talents"],
        "trappings": preview["trappings"],
        "xp_total": preview["xp_total"],
        "xp_spent": preview["xp_spent"],
    }


def roll_career_for_draft(draft: dict[str, Any]) -> dict[str, Any]:
    result = roll_human_career()
    count = draft.get("career_roll_count", 0) + 1
    options = list(draft.get("career_roll_options") or [])
    cid = result["career"]["id"]
    if cid not in options:
        options.append(cid)
    return {
        "roll": result["roll"],
        "career": result["career"],
        "career_roll_count": count,
        "career_roll_options": options,
        "xp_award": 50 if count == 1 else (25 if count == 2 else 0),
    }
