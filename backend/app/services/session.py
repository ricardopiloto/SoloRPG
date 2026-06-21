from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Campaign, CampaignStatus, GameSession, PlayerCharacter, SessionMode, SessionTurn
from app.rules.careers import validate_xp
from app.rules.fate import refresh_fortune_from_fate
from app.services.cloudflare_workers_ai import probe_image_credits


async def pause_session(db: AsyncSession, session: GameSession) -> GameSession:
    if not session.is_active:
        raise ValueError("Sessão não está ativa")
    if session.paused_at is not None:
        raise ValueError("Sessão já está pausada")
    session.paused_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session


async def resume_session(db: AsyncSession, session: GameSession) -> GameSession:
    if not session.is_active:
        raise ValueError("Sessão não está ativa")
    if session.paused_at is None:
        raise ValueError("Sessão não está pausada")
    paused_at = session.paused_at.replace(tzinfo=timezone.utc) if session.paused_at.tzinfo is None else session.paused_at
    delta = int((datetime.now(timezone.utc) - paused_at).total_seconds())
    session.total_paused_seconds = (session.total_paused_seconds or 0) + delta
    session.paused_at = None
    await db.commit()
    await db.refresh(session)
    return session


async def start_session(
    db: AsyncSession,
    campaign_id: UUID,
    duration_minutes: int = 45,
) -> GameSession:
    campaign = await db.scalar(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(selectinload(Campaign.sessions))
    )
    if not campaign or campaign.status != CampaignStatus.ACTIVE:
        raise ValueError("Campanha inválida ou inativa")

    active = await db.scalar(
        select(GameSession).where(
            GameSession.campaign_id == campaign_id, GameSession.is_active.is_(True)
        )
    )
    if active:
        # Return paused session instead of raising an error
        if active.paused_at is not None:
            return active
        raise ValueError("Já existe uma sessão ativa")

    is_first = len(campaign.sessions) == 0
    session = GameSession(
        campaign_id=campaign_id,
        is_first_session=is_first,
        duration_minutes=duration_minutes,
        mode=SessionMode.EXPLORATION,
        is_active=True,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()

    character = await db.scalar(
        select(PlayerCharacter).where(PlayerCharacter.id == campaign.character_id)
    )
    if character:
        character.fortune_current, character.fortune_max = refresh_fortune_from_fate(
            character.fate_current
        )

    await db.commit()
    await db.refresh(session)
    session.images_enabled = await probe_image_credits()
    await db.commit()
    await db.refresh(session)
    return session


def session_time_remaining_minutes(session: GameSession) -> int:
    # If paused, elapsed time is frozen at the moment of pausing
    if session.paused_at is not None:
        paused_at = session.paused_at.replace(tzinfo=timezone.utc) if session.paused_at.tzinfo is None else session.paused_at
        raw_elapsed = (paused_at - session.started_at.replace(tzinfo=timezone.utc)).total_seconds()
    else:
        raw_elapsed = (datetime.now(timezone.utc) - session.started_at.replace(tzinfo=timezone.utc)).total_seconds()
    elapsed = max(0.0, raw_elapsed - (session.total_paused_seconds or 0))
    return max(0, session.duration_minutes - int(elapsed // 60))


def should_end_session(session: GameSession) -> bool:
    return session.paused_at is None and session_time_remaining_minutes(session) <= 0


async def append_turn(
    db: AsyncSession,
    session: GameSession,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> None:
    history = list(session.turn_history or [])
    history.append({"role": role, "content": content, "metadata": metadata or {}})
    session.turn_history = history[-50:]
    db.add(
        SessionTurn(
            session_id=session.id,
            role=role,
            content=content,
            metadata_=metadata,
        )
    )
    await db.commit()


async def enter_combat(db: AsyncSession, session: GameSession, combatants: list[dict]) -> dict:
    from app.rules.combat import roll_initiative

    session.mode = SessionMode.COMBAT
    order = []
    for c in combatants:
        ag = c.get("agility", 30)
        init = roll_initiative(ag)
        order.append({**c, "initiative": init})
    order.sort(key=lambda x: x["initiative"], reverse=True)
    state = {"turn": 1, "order": order, "current_index": 0}
    session.combat_state = state
    await db.commit()
    return state


async def advance_combat_turn(db: AsyncSession, session: GameSession) -> dict:
    state = dict(session.combat_state or {})
    state["turn"] = state.get("turn", 1) + 1
    order = state.get("order", [])
    if order:
        state["current_index"] = (state.get("current_index", 0) + 1) % len(order)
    session.combat_state = state
    await db.commit()
    return state


async def end_combat(db: AsyncSession, session: GameSession) -> None:
    session.mode = SessionMode.EXPLORATION
    session.combat_state = None
    await db.commit()


async def end_session(db: AsyncSession, session: GameSession, xp: int = 0) -> None:
    session.is_active = False
    session.ended_at = datetime.now(timezone.utc)
    session.xp_awarded = validate_xp(xp)
    campaign = await db.scalar(select(Campaign).where(Campaign.id == session.campaign_id))
    if campaign and campaign.character:
        campaign.character.xp_total += session.xp_awarded
    await db.commit()
