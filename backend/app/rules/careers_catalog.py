"""Tier 1 career catalog and Human Reikland roll table (WFRP4e Core, PT-BR)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.rules.dice import roll_d100

_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "careers_catalog.json"
_CACHE: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _CACHE
    if _CACHE is None:
        _CACHE = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    return _CACHE


def list_careers(tier: int = 1) -> list[dict[str, Any]]:
    data = _load()
    return [
        {
            "id": c["id"],
            "name": c["name"],
            "career_group": c["career_group"],
            "class": c["class"],
            "tier": c.get("tier", 1),
        }
        for c in data["careers"]
        if c.get("tier", 1) == tier
    ]


def get_career(career_id: str) -> dict[str, Any] | None:
    for c in _load()["careers"]:
        if c["id"] == career_id:
            return c
    return None


def roll_human_career() -> dict[str, Any]:
    roll = roll_d100()
    table = _load()["human_roll_table"]
    for entry in table:
        if entry["min"] <= roll <= entry["max"]:
            career = get_career(entry["career_id"])
            if career:
                return {"roll": roll, "career": career}
    last = table[-1]
    return {"roll": roll, "career": get_career(last["career_id"])}
