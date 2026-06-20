import hashlib
import math
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Campaign, DiaryEntry, Faction, GameSession, NarrativeEvent, NPC, PlayerCharacter


def build_context_xml(
    campaign: Campaign,
    character: PlayerCharacter,
    session: GameSession,
    memory: dict,
    flags: dict | None = None,
) -> str:
    flags = flags or {}
    attrs = character.attributes or {}
    attr_str = ", ".join(f"{k}: {v}" for k, v in attrs.items())
    skills = ", ".join(
        f"{s.get('name', '?')} (+{s.get('advances', 0)})" for s in (character.skills or [])
    ) or "nenhuma"
    talents = ", ".join(t.get("name", "?") for t in (character.talents or [])) or "nenhum"
    inventory = ", ".join(
        f"{t.get('name', '?')} (enc {t.get('encumbrance', 0)})" for t in (character.trappings or [])
    ) or "vazio"
    career = (character.careers or [{}])[0]
    rep = memory.get("reputation", {})
    rep_str = ", ".join(f"{k}: {v}" for k, v in rep.items()) or "nenhuma"

    return f"""<campanha>
  <tom>{campaign.tone or 'indefinido'}</tom>
  <fase_atual>{campaign.narrative_phase}</fase_atual>
  <objetivo_secreto>{campaign.secret_objective or ''}</objetivo_secreto>
  <estado_do_mundo>{campaign.world_state or ''}</estado_do_mundo>
</campanha>

<personagem>
  <nome>{character.name}</nome>
  <carreira>{career.get('name', 'Desconhecida')} (Tier {career.get('tier', 1)})</carreira>
  <atributos>{attr_str}</atributos>
  <ferimentos>Atuais: {character.wounds_current} / Máximo: {character.wounds_max}</ferimentos>
  <pontos_de_destino>Destino: {character.fate_current}/{character.fate_max} | Fortuna: {character.fortune_current}/{character.fortune_max}</pontos_de_destino>
  <pericias>{skills}</pericias>
  <talentos>{talents}</talentos>
  <inventario>{inventory}</inventario>
  <karma>{character.karma}</karma>
  <reputacao>{rep_str}</reputacao>
  <percepcao_social>{character.social_perception}</percepcao_social>
</personagem>

<memoria>
  <resumo_da_campanha>{campaign.campaign_summary or ''}</resumo_da_campanha>
  <ultimas_sessoes>{memory.get('recent_sessions', '')}</ultimas_sessoes>
  <eventos_relevantes>{memory.get('semantic_events', '')}</eventos_relevantes>
  <npcs_ativos>{memory.get('npcs', '')}</npcs_ativos>
  <ganchos_pendentes>{memory.get('hooks', '')}</ganchos_pendentes>
</memoria>

<sessao>
  <modo>{session.mode.value}</modo>
  <tempo_restante>{memory.get('time_remaining_minutes', session.duration_minutes)}</tempo_restante>
  <turno_de_combate>{memory.get('combat_turn', 0)}</turno_de_combate>
  <historico_recente>{memory.get('turn_history', '')}</historico_recente>
  <primeira_sessao>{str(flags.get('primeira_sessao', False)).lower()}</primeira_sessao>
  <encerrar_sessao>{str(flags.get('encerrar_sessao', False)).lower()}</encerrar_sessao>
</sessao>"""


def simple_embedding(text: str, dims: int = 384) -> list[float]:
    """Deterministic lightweight embedding for MVP semantic search without external API."""
    vec = [0.0] * dims
    tokens = text.lower().split()
    for token in tokens:
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        idx = h % dims
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _embedding_vector(embedding) -> list[float] | None:
    if embedding is None:
        return None
    if isinstance(embedding, list):
        return embedding
    return list(embedding)


class SemanticSearchAdapter(ABC):
    @abstractmethod
    async def rank_events(
        self, db: AsyncSession, campaign_id, query: str, limit: int
    ) -> list[NarrativeEvent]:
        pass


class PythonSearchAdapter(SemanticSearchAdapter):
    """Cosine similarity in Python — used for sqlite-dev."""

    async def rank_events(
        self, db: AsyncSession, campaign_id, query: str, limit: int
    ) -> list[NarrativeEvent]:
        events = (
            await db.scalars(
                select(NarrativeEvent)
                .where(NarrativeEvent.campaign_id == campaign_id)
                .order_by(NarrativeEvent.created_at.desc())
                .limit(limit * 4)
            )
        ).all()
        q_emb = simple_embedding(query)
        scored: list[tuple[float, NarrativeEvent]] = []
        for ev in events:
            emb = _embedding_vector(ev.embedding)
            if emb:
                scored.append((_cosine_similarity(q_emb, emb), ev))
            else:
                scored.append((0.0, ev))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ev for _, ev in scored[:limit]]


class PgVectorSearchAdapter(SemanticSearchAdapter):
    """pgvector distance query — used for postgres/supabase."""

    async def rank_events(
        self, db: AsyncSession, campaign_id, query: str, limit: int
    ) -> list[NarrativeEvent]:
        q_emb = simple_embedding(query)
        vec_literal = "[" + ",".join(str(v) for v in q_emb) + "]"
        result = await db.execute(
            text(
                """
                SELECT id FROM narrative_events
                WHERE campaign_id = :campaign_id AND embedding IS NOT NULL
                ORDER BY embedding <=> :query_vec
                LIMIT :lim
                """
            ),
            {"campaign_id": campaign_id, "query_vec": vec_literal, "lim": limit},
        )
        ids = [row[0] for row in result.fetchall()]
        if not ids:
            return (
                await db.scalars(
                    select(NarrativeEvent)
                    .where(NarrativeEvent.campaign_id == campaign_id)
                    .order_by(NarrativeEvent.created_at.desc())
                    .limit(limit)
                )
            ).all()
        events = (
            await db.scalars(select(NarrativeEvent).where(NarrativeEvent.id.in_(ids)))
        ).all()
        order = {eid: i for i, eid in enumerate(ids)}
        events.sort(key=lambda e: order.get(e.id, 999))
        return events


def get_semantic_search() -> SemanticSearchAdapter:
    if settings.is_postgres:
        return PgVectorSearchAdapter()
    return PythonSearchAdapter()


async def load_memory_context(
    db: AsyncSession,
    campaign: Campaign,
    session: GameSession,
    query: str = "",
) -> dict:
    npcs = (
        await db.scalars(select(NPC).where(NPC.campaign_id == campaign.id))
    ).all()
    factions = (
        await db.scalars(select(Faction).where(Faction.campaign_id == campaign.id))
    ).all()

    recent_sessions = (
        await db.scalars(
            select(GameSession)
            .where(GameSession.campaign_id == campaign.id, GameSession.id != session.id)
            .order_by(GameSession.started_at.desc())
            .limit(3)
        )
    ).all()

    search = get_semantic_search()
    if query:
        events = await search.rank_events(
            db, campaign.id, query, settings.semantic_memory_limit
        )
    else:
        events = (
            await db.scalars(
                select(NarrativeEvent)
                .where(NarrativeEvent.campaign_id == campaign.id)
                .order_by(NarrativeEvent.created_at.desc())
                .limit(settings.semantic_memory_limit)
            )
        ).all()

    elapsed = (datetime.now(timezone.utc) - session.started_at.replace(tzinfo=timezone.utc)).total_seconds()
    remaining = max(0, session.duration_minutes - int(elapsed // 60))

    turn_history = session.turn_history or []
    recent_turns = turn_history[-settings.session_turn_history_limit :]

    return {
        "recent_sessions": "\n".join(
            s.player_summary or "" for s in recent_sessions if s.player_summary
        ),
        "semantic_events": "\n".join(e.description for e in events),
        "npcs": "\n".join(
            f"{n.name} ({n.role}): {n.relationship_status}" for n in npcs
        ),
        "hooks": campaign.world_state or "",
        "reputation": {f.name: f.reputation for f in factions},
        "time_remaining_minutes": remaining,
        "combat_turn": (session.combat_state or {}).get("turn", 0),
        "turn_history": "\n".join(
            f"{t.get('role', '?')}: {t.get('content', '')}" for t in recent_turns
        ),
    }


async def persist_session_summary(
    db: AsyncSession,
    campaign: Campaign,
    session: GameSession,
    player_summary: str,
    system_summary: dict,
) -> None:
    session.player_summary = player_summary
    session.system_summary = system_summary
    session.is_active = False
    session.ended_at = datetime.now(timezone.utc)

    if player_summary:
        db.add(
            DiaryEntry(
                campaign_id=campaign.id,
                session_id=session.id,
                content=player_summary,
            )
        )

    for event_desc in system_summary.get("eventos_principais", []):
        emb = simple_embedding(event_desc)
        db.add(
            NarrativeEvent(
                campaign_id=campaign.id,
                session_id=session.id,
                event_type="session_event",
                description=event_desc,
                embedding=emb,
            )
        )

    for npc_data in system_summary.get("npcs_interagidos", []):
        name = npc_data.get("nome")
        if not name:
            continue
        existing = await db.scalar(
            select(NPC).where(NPC.campaign_id == campaign.id, NPC.name == name)
        )
        if existing:
            existing.relationship_status = npc_data.get("status_relacao", existing.relationship_status)
            if npc_data.get("nome_conhecido"):
                existing.known_name = npc_data["nome_conhecido"]
            if npc_data.get("local"):
                existing.met_location = npc_data["local"]
        else:
            db.add(
                NPC(
                    campaign_id=campaign.id,
                    name=name,
                    known_name=npc_data.get("nome_conhecido") or name,
                    met_location=npc_data.get("local"),
                    relationship_status=npc_data.get("status_relacao", "neutro"),
                )
            )

    karma_delta = system_summary.get("karma_delta", 0)
    char = await db.scalar(
        select(PlayerCharacter).where(PlayerCharacter.id == campaign.character_id)
    )
    if char:
        if karma_delta:
            char.karma = max(-100, min(100, char.karma + karma_delta))

        perception = system_summary.get("percepcao_social")
        if perception:
            char.social_perception = str(perception)[:2000]

    for faction_name, delta in (system_summary.get("reputacao_delta") or {}).items():
        faction = await db.scalar(
            select(Faction).where(
                Faction.campaign_id == campaign.id, Faction.name == faction_name
            )
        )
        if faction:
            faction.reputation = max(-100, min(100, faction.reputation + delta))
        else:
            db.add(
                Faction(
                    campaign_id=campaign.id,
                    name=faction_name,
                    reputation=max(-100, min(100, delta)),
                )
            )

    world = system_summary.get("estado_mundo")
    if world:
        campaign.world_state = world

    hooks = system_summary.get("ganchos_abertos")
    if hooks:
        campaign.campaign_summary = (campaign.campaign_summary or "") + "\n" + "\n".join(hooks)

    await db.commit()
