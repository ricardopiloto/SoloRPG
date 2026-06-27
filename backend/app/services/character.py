import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.db.models import Campaign, CampaignStatus, CharacterStatus, PlayerCharacter
from app.rules.careers import (
    PROGRESSION_SKILLS,
    PROGRESSION_TALENTS,
    SKILL_ADVANCE_COST,
    TALENT_COST,
    apply_skill_advance,
    reverse_skill_advance,
    reverse_talent,
    skill_advances_by_name,
    xp_available,
)

PRE_GENERATED_CHARACTERS = [
    {
        "name": "Helena Krauss",
        "background": "Ex-soldado imperial desiludida",
        "attributes": {"WS": 42, "BS": 33, "S": 35, "T": 38, "I": 32, "Ag": 34, "Dex": 28, "Int": 29, "WP": 31, "Fel": 27},
        "wounds_max": 12,
        "fate_max": 3,
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
        "careers": [{"name": "Aprendiz", "tier": 1, "advances_spent": 0}],
        "skills": [{"name": "Conhecimento (Magia)", "advances": 2, "linked_attribute": "Int"}],
        "talents": [{"name": "Leitura Apressada"}],
        "trappings": [{"name": "Grimório", "encumbrance": 1, "description": "Páginas amareladas"}],
    },
]


def _record_progression_purchase(char: PlayerCharacter, purchase_type: str, cost: int, **fields) -> None:
    if not char.progression_source_session_id:
        return
    budget = char.progression_refund_budget or 0
    refundable = min(cost, budget)
    char.progression_refund_budget = budget - refundable
    purchases = list(char.progression_purchases or [])
    purchases.append(
        {
            "id": str(uuid.uuid4()),
            "type": purchase_type,
            "cost": cost,
            "refundable_xp": refundable,
            "refunded": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **fields,
        }
    )
    char.progression_purchases = purchases
    flag_modified(char, "progression_purchases")


def close_progression_refund_window(char: PlayerCharacter) -> None:
    char.progression_source_session_id = None
    char.progression_refund_budget = 0
    char.progression_purchases = []
    flag_modified(char, "progression_purchases")


def open_progression_refund_window(
    char: PlayerCharacter, session_id: UUID, xp_awarded: int
) -> None:
    char.progression_source_session_id = session_id
    char.progression_refund_budget = xp_awarded
    char.progression_purchases = []
    flag_modified(char, "progression_purchases")


async def create_character(
    db: AsyncSession,
    data: dict,
    *,
    user_id: UUID | None = None,
    is_starter: bool = False,
) -> PlayerCharacter:
    char = PlayerCharacter(
        user_id=user_id,
        is_starter=is_starter,
        name=data["name"],
        background=data.get("background"),
        attributes=data.get("attributes", {}),
        wounds_current=data.get("wounds_max", 10),
        wounds_max=data.get("wounds_max", 10),
        fate_current=data.get("fate_max", 2),
        fate_max=data.get("fate_max", 2),
        fortune_current=data.get("fate_max", 2),
        fortune_max=data.get("fate_max", 2),
        careers=data.get("careers", []),
        skills=data.get("skills", []),
        talents=data.get("talents", []),
        trappings=data.get("trappings", []),
        xp_total=data.get("xp_total", 0),
        xp_spent=data.get("xp_spent", 0),
    )
    db.add(char)
    await db.commit()
    await db.refresh(char)
    return char


async def create_from_pregen(
    db: AsyncSession, template_index: int, name: str | None, user_id: UUID
) -> PlayerCharacter:
    if template_index < 0 or template_index >= len(PRE_GENERATED_CHARACTERS):
        raise ValueError("Template inválido")
    data = dict(PRE_GENERATED_CHARACTERS[template_index])
    if name:
        data["name"] = name
    return await create_character(db, data, user_id=user_id)


async def get_character(db: AsyncSession, character_id: UUID) -> PlayerCharacter | None:
    return await db.scalar(select(PlayerCharacter).where(PlayerCharacter.id == character_id))


async def list_characters(db: AsyncSession, user_id: UUID) -> list[PlayerCharacter]:
    return list(
        await db.scalars(
            select(PlayerCharacter)
            .where(PlayerCharacter.user_id == user_id)
            .order_by(PlayerCharacter.created_at.desc())
        )
    )


async def purchase_skill_advance(
    db: AsyncSession, character_id: UUID, skill_name: str, linked_attribute: str
) -> PlayerCharacter:
    char = await get_character(db, character_id)
    if not char or char.status != CharacterStatus.ALIVE:
        raise ValueError("Personagem inválido")
    if xp_available(char.xp_total, char.xp_spent) < SKILL_ADVANCE_COST:
        raise ValueError("XP insuficiente")
    char.skills = apply_skill_advance(char.skills or [], skill_name, linked_attribute)
    flag_modified(char, "skills")
    char.xp_spent += SKILL_ADVANCE_COST
    _record_progression_purchase(
        char,
        "skill",
        SKILL_ADVANCE_COST,
        skill_name=skill_name,
        linked_attribute=linked_attribute,
        talent_name=None,
    )
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
    flag_modified(char, "talents")
    char.xp_spent += TALENT_COST
    _record_progression_purchase(
        char,
        "talent",
        TALENT_COST,
        skill_name=None,
        linked_attribute=None,
        talent_name=talent_name,
    )
    await db.commit()
    await db.refresh(char)
    return char


async def refund_progression_purchase(
    db: AsyncSession, character_id: UUID, purchase_id: UUID
) -> PlayerCharacter:
    char = await get_character(db, character_id)
    if not char or char.status != CharacterStatus.ALIVE:
        raise ValueError("Personagem inválido")
    if not char.progression_source_session_id:
        raise ValueError("Janela de devolução encerrada")

    purchases = list(char.progression_purchases or [])
    entry = next((p for p in purchases if p.get("id") == str(purchase_id)), None)
    if not entry or entry.get("refunded"):
        raise ValueError("Compra não encontrada ou já devolvida")
    if entry.get("refundable_xp", 0) <= 0:
        raise ValueError("Compra não reembolsável")

    purchase_type = entry.get("type")
    if purchase_type == "skill":
        char.skills = reverse_skill_advance(char.skills or [], entry["skill_name"])
        flag_modified(char, "skills")
    elif purchase_type == "talent":
        char.talents = reverse_talent(char.talents or [], entry["talent_name"])
        flag_modified(char, "talents")
    else:
        raise ValueError("Tipo de compra inválido")

    refundable = entry["refundable_xp"]
    char.xp_spent -= entry["cost"]
    char.progression_refund_budget = (char.progression_refund_budget or 0) + refundable
    entry["refunded"] = True
    char.progression_purchases = purchases
    flag_modified(char, "progression_purchases")
    await db.commit()
    await db.refresh(char)
    return char


def _refund_budget_total(char: PlayerCharacter) -> int:
    budget = char.progression_refund_budget or 0
    attributed = sum(
        p.get("refundable_xp", 0)
        for p in (char.progression_purchases or [])
        if not p.get("refunded")
    )
    return budget + attributed


async def get_progression_options(db: AsyncSession, character_id: UUID) -> dict:
    char = await get_character(db, character_id)
    if not char:
        raise ValueError("Personagem não encontrado")
    avail = xp_available(char.xp_total, char.xp_spent)
    owned_skills = skill_advances_by_name(char.skills)
    owned_talents = {t.get("name") for t in (char.talents or [])}
    window_active = char.progression_source_session_id is not None
    purchases = char.progression_purchases or []
    refundable_purchases = [
        {
            "id": p["id"],
            "type": p["type"],
            "skill_name": p.get("skill_name"),
            "linked_attribute": p.get("linked_attribute"),
            "talent_name": p.get("talent_name"),
            "cost": p["cost"],
            "refundable_xp": p.get("refundable_xp", 0),
            "refunded": p.get("refunded", False),
        }
        for p in purchases
        if not p.get("refunded") and p.get("refundable_xp", 0) > 0
    ]
    return {
        "character_id": str(char.id),
        "xp_available": avail,
        "progression_window_active": window_active,
        "refund_budget_remaining": char.progression_refund_budget or 0,
        "refund_budget_total": _refund_budget_total(char) if window_active else 0,
        "refundable_purchases": refundable_purchases,
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
