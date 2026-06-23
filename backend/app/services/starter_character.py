import secrets
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PlayerCharacter
from app.rules.character_creation import (
    CAREER_SKILL_MAX,
    draft_to_character_data,
    roll_all_characteristics,
    roll_career_for_draft,
    validate_draft,
)
from app.services.character import create_character


def _build_random_draft() -> dict:
    draft: dict = {
        "species_id": "human",
        "species_method": "choose",
        "career_method": "roll",
        "career_roll_count": 0,
        "career_roll_options": [],
        "attributes_method": "roll",
        "attribute_rolls": roll_all_characteristics(),
        "attribute_advances": {},
        "attributes_swapped": False,
        "attributes_rerolled": False,
        "fate_allotted": 2,
        "species_skills": {},
        "species_talents": [],
    }

    career_roll = roll_career_for_draft(draft)
    career = career_roll["career"]
    draft.update(
        {
            "career_id": career["id"],
            "career_roll_count": career_roll["career_roll_count"],
            "career_roll_options": career_roll["career_roll_options"],
        }
    )

    career_skills = career.get("skills") or []
    points_left = 40
    allocation: dict[str, int] = {}
    for skill in career_skills:
        if points_left <= 0:
            break
        take = min(CAREER_SKILL_MAX, points_left)
        allocation[skill] = take
        points_left -= take
    draft["career_skills"] = allocation
    draft["career_talent"] = (career.get("talents") or ["Resolução"])[0]

    suffix = secrets.randbelow(9000) + 1000
    draft["name"] = f"{career['name']} de Reikland #{suffix}"
    draft["background"] = None

    errors = validate_draft(draft, final=True)
    if errors:
        raise ValueError(f"Rascunho starter inválido: {errors[0]['message']}")
    return draft


async def user_has_starter(db: AsyncSession, user_id: UUID) -> bool:
    existing = await db.scalar(
        select(PlayerCharacter).where(
            PlayerCharacter.user_id == user_id,
            PlayerCharacter.is_starter.is_(True),
        )
    )
    return existing is not None


async def generate_random_starter_character(db: AsyncSession, user_id: UUID) -> PlayerCharacter:
    if await user_has_starter(db, user_id):
        raise ValueError("Personagem inicial já existe")

    draft = _build_random_draft()
    data = draft_to_character_data(draft)
    return await create_character(db, data, user_id=user_id, is_starter=True)
