from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Campaign, CampaignStatus, CharacterStatus, PlayerCharacter
from app.rules.careers import (
    PROGRESSION_SKILLS,
    PROGRESSION_TALENTS,
    SKILL_ADVANCE_COST,
    TALENT_COST,
    apply_skill_advance,
    xp_available,
)

PRE_GENERATED_CHARACTERS = [
    {
        "name": "Helena Krauss",
        "background": "Ex-soldado imperial desiludida",
        "attributes": {"WS": 42, "BS": 33, "S": 35, "T": 38, "I": 32, "Ag": 34, "Dex": 28, "Int": 29, "WP": 31, "Fel": 27},
        "wounds_max": 12,
        "fate_max": 3,
        "fortune_max": 2,
        "careers": [{"name": "Soldado", "tier": 1, "advances_spent": 0}],
        "skills": [{"name": "Armas Corpo a Corpo (Básicas)", "advances": 1, "linked_attribute": "WS"}],
        "talents": [{"name": "Resolução"}],
        "trappings": [{"name": "Espada Longa", "encumbrance": 1, "description": "Aço imperial"}],
    },
    {
        "name": "Tobias Grimm",
        "background": "Aprendiz de mago expulso da academia",
        "attributes": {"WS": 25, "BS": 28, "S": 22, "T": 24, "I": 40, "Ag": 30, "Dex": 33, "Int": 45, "WP": 38, "Fel": 30},
        "wounds_max": 9,
        "fate_max": 2,
        "fortune_max": 1,
        "careers": [{"name": "Aprendiz", "tier": 1, "advances_spent": 0}],
        "skills": [{"name": "Conhecimento (Magia)", "advances": 2, "linked_attribute": "Int"}],
        "talents": [{"name": "Leitura Apressada"}],
        "trappings": [{"name": "Grimório", "encumbrance": 1, "description": "Páginas amareladas"}],
    },
]


async def create_character(db: AsyncSession, data: dict) -> PlayerCharacter:
    char = PlayerCharacter(
        name=data["name"],
        background=data.get("background"),
        attributes=data.get("attributes", {}),
        wounds_current=data.get("wounds_max", 10),
        wounds_max=data.get("wounds_max", 10),
        fate_current=data.get("fate_max", 2),
        fate_max=data.get("fate_max", 2),
        fortune_current=data.get("fortune_max", 1),
        fortune_max=data.get("fortune_max", 1),
        careers=data.get("careers", []),
        skills=data.get("skills", []),
        talents=data.get("talents", []),
        trappings=data.get("trappings", []),
    )
    db.add(char)
    await db.commit()
    await db.refresh(char)
    return char


async def create_from_pregen(db: AsyncSession, template_index: int, name: str | None = None) -> PlayerCharacter:
    if template_index < 0 or template_index >= len(PRE_GENERATED_CHARACTERS):
        raise ValueError("Template inválido")
    data = dict(PRE_GENERATED_CHARACTERS[template_index])
    if name:
        data["name"] = name
    return await create_character(db, data)


async def get_character(db: AsyncSession, character_id: UUID) -> PlayerCharacter | None:
    return await db.scalar(select(PlayerCharacter).where(PlayerCharacter.id == character_id))


async def list_characters(db: AsyncSession) -> list[PlayerCharacter]:
    return list(await db.scalars(select(PlayerCharacter).order_by(PlayerCharacter.created_at.desc())))


async def purchase_skill_advance(
    db: AsyncSession, character_id: UUID, skill_name: str, linked_attribute: str
) -> PlayerCharacter:
    char = await get_character(db, character_id)
    if not char or char.status != CharacterStatus.ALIVE:
        raise ValueError("Personagem inválido")
    if xp_available(char.xp_total, char.xp_spent) < SKILL_ADVANCE_COST:
        raise ValueError("XP insuficiente")
    char.skills = apply_skill_advance(char.skills or [], skill_name, linked_attribute)
    char.xp_spent += SKILL_ADVANCE_COST
    await db.commit()
    await db.refresh(char)
    return char


async def purchase_talent(db: AsyncSession, character_id: UUID, talent_name: str) -> PlayerCharacter:
    char = await get_character(db, character_id)
    if not char or char.status != CharacterStatus.ALIVE:
        raise ValueError("Personagem inválido")
    if any(t.get("name") == talent_name for t in (char.talents or [])):
        raise ValueError("Talento já possuído")
    if xp_available(char.xp_total, char.xp_spent) < TALENT_COST:
        raise ValueError("XP insuficiente")
    talents = list(char.talents or [])
    talents.append({"name": talent_name})
    char.talents = talents
    char.xp_spent += TALENT_COST
    await db.commit()
    await db.refresh(char)
    return char


async def get_progression_options(db: AsyncSession, character_id: UUID) -> dict:
    char = await get_character(db, character_id)
    if not char:
        raise ValueError("Personagem não encontrado")
    avail = xp_available(char.xp_total, char.xp_spent)
    owned_skills = {s.get("name"): s.get("advances", 0) for s in (char.skills or [])}
    owned_talents = {t.get("name") for t in (char.talents or [])}
    return {
        "character_id": str(char.id),
        "xp_available": avail,
        "skills": [
            {
                "name": s["name"],
                "linked_attribute": s["linked_attribute"],
                "cost": SKILL_ADVANCE_COST,
                "current_advances": owned_skills.get(s["name"], 0),
                "affordable": avail >= SKILL_ADVANCE_COST,
            }
            for s in PROGRESSION_SKILLS
        ],
        "talents": [
            {
                "name": name,
                "cost": TALENT_COST,
                "owned": name in owned_talents,
                "affordable": avail >= TALENT_COST and name not in owned_talents,
            }
            for name in PROGRESSION_TALENTS
        ],
    }
