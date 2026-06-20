"""Canonical WFRP skill catalog for MVP."""

SKILL_CATALOG: dict[str, str] = {
    "Arrombamento": "Dex",
    "Atirar (Arco)": "BS",
    "Atirar (Armas de Fogo)": "BS",
    "Atirar (Bestas)": "BS",
    "Atirar (Pistolas)": "BS",
    "Atletismo": "Ag",
    "Charme": "Fel",
    "Conhecimento (Reikland)": "Int",
    "Escalar": "S",
    "Esquivar": "Ag",
    "Furtividade": "Ag",
    "Intimidação": "S",
    "Liderança": "Fel",
    "Luta": "WS",
    "Natação": "S",
    "Navegação": "I",
    "Orientação": "I",
    "Percepção": "I",
    "Vontade": "WP",
}

PROGRESSION_SKILL_NAMES = [
    "Atletismo",
    "Percepção",
    "Furtividade",
    "Luta",
    "Atirar (Arco)",
    "Conhecimento (Reikland)",
    "Intimidação",
    "Charme",
    "Vontade",
    "Escalar",
]


def list_skills() -> list[dict[str, str]]:
    return [
        {"name": name, "linked_attribute": SKILL_CATALOG[name]}
        for name in sorted(SKILL_CATALOG.keys())
    ]
