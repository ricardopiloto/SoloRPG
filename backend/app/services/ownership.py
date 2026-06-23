from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Campaign, GameSession, PlayerCharacter, User


async def get_owned_character(
    db: AsyncSession, user: User, character_id: UUID
) -> PlayerCharacter:
    char = await db.scalar(select(PlayerCharacter).where(PlayerCharacter.id == character_id))
    if not char:
        raise HTTPException(404, "Personagem não encontrado")
    if char.user_id != user.id:
        raise HTTPException(403, "Acesso negado a este personagem")
    return char


async def get_owned_campaign(db: AsyncSession, user: User, campaign_id: UUID) -> Campaign:
    campaign = await db.scalar(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(selectinload(Campaign.character))
    )
    if not campaign:
        raise HTTPException(404, "Campanha não encontrada")
    if not campaign.character or campaign.character.user_id != user.id:
        raise HTTPException(403, "Acesso negado a esta campanha")
    return campaign


async def get_owned_session(db: AsyncSession, user: User, session_id: UUID) -> GameSession:
    session = await db.scalar(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(selectinload(GameSession.campaign).selectinload(Campaign.character))
    )
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    character = session.campaign.character if session.campaign else None
    if not character or character.user_id != user.id:
        raise HTTPException(403, "Acesso negado a esta sessão")
    return session
