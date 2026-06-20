import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Campaign, CampaignStatus, CharacterStatus, GameSession, NPC, PlayerCharacter


async def create_campaign(db: AsyncSession, character_id: UUID) -> Campaign:
    char = await db.scalar(select(PlayerCharacter).where(PlayerCharacter.id == character_id))
    if not char or char.status != CharacterStatus.ALIVE:
        raise ValueError("Personagem inválido ou morto")

    existing = await db.scalar(
        select(Campaign).where(
            Campaign.character_id == character_id,
            Campaign.status == CampaignStatus.ACTIVE,
        )
    )
    if existing:
        raise ValueError("Personagem já possui campanha ativa")

    campaign = Campaign(character_id=character_id, status=CampaignStatus.ACTIVE)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    campaign.character = char
    return campaign


async def get_campaign(db: AsyncSession, campaign_id: UUID) -> Campaign | None:
    return await db.scalar(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(selectinload(Campaign.character), selectinload(Campaign.sessions))
    )


async def list_campaigns(db: AsyncSession, status: CampaignStatus | None = None) -> list[Campaign]:
    q = select(Campaign).options(selectinload(Campaign.character)).order_by(Campaign.created_at.desc())
    if status:
        q = q.where(Campaign.status == status)
    return list(await db.scalars(q))


async def apply_nova_campanha(db: AsyncSession, campaign: Campaign, payload: dict) -> Campaign:
    campaign.tone = payload.get("tom")
    campaign.secret_objective = payload.get("objetivo_secreto")
    antagonista = payload.get("antagonista")
    campaign.antagonist = (
        json.dumps(antagonista, ensure_ascii=False)
        if isinstance(antagonista, dict)
        else antagonista
    )
    campaign.opening_location = payload.get("localizacao_abertura")
    campaign.world_state = payload.get("ponto_de_partida") or payload.get("gancho_inicial")
    opening = campaign.opening_location

    for npc in payload.get("npcs_iniciais", []):
        nome = npc.get("nome", "Desconhecido")
        db.add(
            NPC(
                campaign_id=campaign.id,
                name=nome,
                known_name=npc.get("nome_conhecido") or nome,
                met_location=npc.get("local") or opening,
                role=npc.get("papel"),
                secret=npc.get("segredo"),
                relationship_status=npc.get("relacao", "neutro"),
            )
        )

    hooks = payload.get("ganchos_ocultos", [])
    if hooks:
        campaign.campaign_summary = "[GANCHOS OCULTOS]\n" + "\n".join(f"- {h}" for h in hooks)

    await db.commit()
    await db.refresh(campaign)
    return campaign


async def list_campaign_npcs(db: AsyncSession, campaign_id: UUID) -> list[NPC]:
    npcs = list(await db.scalars(select(NPC).where(NPC.campaign_id == campaign_id)))
    return sorted(npcs, key=lambda n: (n.known_name or n.name).lower())


async def get_active_session(db: AsyncSession, campaign_id: UUID) -> GameSession | None:
    return await db.scalar(
        select(GameSession).where(
            GameSession.campaign_id == campaign_id,
            GameSession.is_active.is_(True),
        )
    )


async def mark_campaign_completed(db: AsyncSession, campaign_id: UUID) -> Campaign:
    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        raise ValueError("Campanha não encontrada")
    campaign.status = CampaignStatus.COMPLETED
    await db.commit()
    return campaign


async def mark_campaign_unfinished(db: AsyncSession, campaign_id: UUID, death_cause: str) -> Campaign:
    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        raise ValueError("Campanha não encontrada")
    campaign.status = CampaignStatus.UNFINISHED
    campaign.world_state = (campaign.world_state or "") + f"\n[MORTE] {death_cause}"
    await db.commit()
    return campaign
