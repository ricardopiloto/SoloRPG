from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_verified_user, require_custom_chargen_enabled
from app.db.database import get_db
from app.db.models import User
from app.schemas.api import (
    BackgroundGenerateOut,
    BackgroundGenerateRequest,
    CampaignCreate,
    CampaignOut,
    CampaignNpcListOut,
    CareerDetailOut,
    CareerListOut,
    CharacterCreate,
    CharacterCreationSubmit,
    CharacterCreationValidateOut,
    CharacterOut,
    CreationOptionsOut,
    PlayerAction,
    PregenCreate,
    ProgressionOptionsOut,
    ProgressionSkill,
    ProgressionTalent,
    QuickRollRequest,
    QuickRollResponse,
    RollRequest,
    RollResponse,
    ImageJobOut,
    SessionDetailOut,
    SessionOut,
    SessionStart,
    SessionTurnOut,
    SkillCatalogOut,
    TurnResponse,
)
from app.services.campaign import (
    create_campaign,
    get_active_session,
    get_campaign,
    list_campaign_npcs,
    list_campaigns,
    mark_campaign_completed,
)
from app.services.character import (
    PRE_GENERATED_CHARACTERS,
    create_character,
    create_from_pregen,
    get_character,
    get_progression_options,
    list_characters,
    purchase_skill_advance,
    purchase_talent,
)
from app.services.gm_orchestrator import GMOrchestrator
from app.services.ownership import get_owned_campaign, get_owned_character, get_owned_session
from app.services.session import (
    pause_session,
    resume_session,
    session_time_remaining_minutes,
    start_session,
)

router = APIRouter()
gm = GMOrchestrator()


def _campaign_out(c, active_session=None) -> CampaignOut:
    return CampaignOut(
        id=c.id,
        character_id=c.character_id,
        status=c.status.value,
        tone=c.tone,
        opening_location=c.opening_location,
        world_state=c.world_state,
        created_at=c.created_at,
        character_name=c.character.name if c.character else None,
        active_session_id=active_session.id if active_session else None,
        active_session_paused=bool(active_session and active_session.paused_at is not None),
        active_session_time_remaining=session_time_remaining_minutes(active_session) if active_session else None,
    )


async def _campaign_out_with_session(db: AsyncSession, c) -> CampaignOut:
    active = await get_active_session(db, c.id)
    return _campaign_out(c, active)


def _session_out(s) -> SessionOut:
    return SessionOut(
        id=s.id,
        campaign_id=s.campaign_id,
        mode=s.mode.value,
        is_active=s.is_active,
        is_first_session=s.is_first_session,
        duration_minutes=s.duration_minutes,
        time_remaining_minutes=session_time_remaining_minutes(s),
        started_at=s.started_at,
        turn_phase=s.turn_phase,
        combat_state=s.combat_state,
        paused_at=s.paused_at,
        images_enabled=bool(s.images_enabled),
    )


def _turn_response(result, session) -> TurnResponse:
    return TurnResponse(
        narrative=result.narrative,
        roll_results=result.roll_results,
        images=result.images,
        session_ended=result.session_ended,
        xp_awarded=result.xp_awarded,
        player_summary=result.player_summary,
        time_remaining_minutes=session_time_remaining_minutes(session) if session else 0,
        mode=session.mode.value if session else "EXPLORACAO",
        turn_phase=session.turn_phase if session else "normal",
        pending_test=session.pending_test if session else None,
        combat_state=session.combat_state if session else None,
        scene_mood=getattr(result, "scene_mood", None),
    )


def _session_detail(session, campaign) -> SessionDetailOut:
    base = _session_out(session)
    return SessionDetailOut(
        **base.model_dump(),
        character_id=campaign.character_id if campaign else None,
        character_name=campaign.character.name if campaign and campaign.character else None,
        opening_location=campaign.opening_location if campaign else None,
        tone=campaign.tone if campaign else None,
    )


@router.get("/rules/skills", response_model=SkillCatalogOut)
async def api_list_skills():
    from app.rules.skills import list_skills

    return {"skills": list_skills()}


@router.get("/rules/character-creation", response_model=CreationOptionsOut)
async def api_creation_options():
    from app.rules.species import creation_options

    return {"options": creation_options()}


@router.get("/rules/careers", response_model=CareerListOut)
async def api_list_careers(tier: int = 1):
    from app.rules.careers_catalog import list_careers

    careers = list_careers(tier=tier)
    return {
        "careers": [
            {
                "id": c["id"],
                "name": c["name"],
                "career_group": c["career_group"],
                "class": c["class"],
                "tier": c.get("tier", 1),
            }
            for c in careers
        ]
    }


@router.get("/rules/careers/{career_id}", response_model=CareerDetailOut)
async def api_get_career(career_id: str):
    from app.rules.careers_catalog import get_career

    career = get_career(career_id)
    if not career:
        raise HTTPException(404, "Carreira não encontrada")
    return {
        "id": career["id"],
        "name": career["name"],
        "career_group": career["career_group"],
        "class": career["class"],
        "tier": career.get("tier", 1),
        "skills": career["skills"],
        "talents": career["talents"],
        "trappings": career["trappings"],
    }


@router.post("/characters/validate-creation", response_model=CharacterCreationValidateOut)
async def api_validate_creation(
    body: CharacterCreationSubmit,
    _: None = Depends(require_custom_chargen_enabled),
):
    from app.rules.character_creation import compute_preview, validate_draft

    draft = body.draft.model_dump()
    errors = validate_draft(draft, final=False)
    computed = compute_preview(draft) if draft.get("career_id") else None
    return {"valid": len(errors) == 0, "errors": errors, "computed": computed}


@router.post("/characters/creation/roll-attributes")
async def api_roll_attributes(_: None = Depends(require_custom_chargen_enabled)):
    from app.rules.character_creation import roll_all_characteristics

    return {"attributes": roll_all_characteristics()}


@router.post("/characters/creation/roll-career")
async def api_roll_career(
    body: CharacterCreationSubmit,
    _: None = Depends(require_custom_chargen_enabled),
):
    from app.rules.character_creation import roll_career_for_draft

    return roll_career_for_draft(body.draft.model_dump())


@router.post("/characters/creation/roll-species-talent")
async def api_roll_species_talent(
    body: CharacterCreationSubmit,
    _: None = Depends(require_custom_chargen_enabled),
):
    from app.rules.character_creation import roll_species_talent

    species_id = body.draft.species_id or "human"
    return {"talent": roll_species_talent(species_id)}


@router.post("/characters/generate-background", response_model=BackgroundGenerateOut)
async def api_generate_background(
    body: BackgroundGenerateRequest,
    user: User = Depends(get_verified_user),
    _: None = Depends(require_custom_chargen_enabled),
):
    from app.services.character_background import generate_background

    try:
        background = await generate_background(body.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:
        raise HTTPException(502, f"Falha ao gerar background: {e}") from e
    return {"background": background}


@router.get("/characters/pregen")
async def list_pregen(user: User = Depends(get_verified_user)):
    return [
        {"index": i, "name": c["name"], "background": c["background"], "career": c["careers"][0]["name"]}
        for i, c in enumerate(PRE_GENERATED_CHARACTERS)
    ]


@router.post("/characters", response_model=CharacterOut)
async def api_create_character(
    body: CharacterCreationSubmit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
    _: None = Depends(require_custom_chargen_enabled),
):
    from app.rules.character_creation import draft_to_character_data

    try:
        data = draft_to_character_data(body.draft.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    char = await create_character(db, data, user_id=user.id)
    return char


@router.post("/characters/pregen", response_model=CharacterOut)
async def api_create_pregen(
    body: PregenCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    try:
        return await create_from_pregen(db, body.template_index, body.name, user.id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/characters", response_model=list[CharacterOut])
async def api_list_characters(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    return await list_characters(db, user.id)


@router.get("/characters/{character_id}", response_model=CharacterOut)
async def api_get_character(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    return await get_owned_character(db, user, character_id)


@router.post("/characters/{character_id}/progression/skill", response_model=CharacterOut)
async def api_progression_skill(
    character_id: UUID,
    body: ProgressionSkill,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_character(db, user, character_id)
    try:
        return await purchase_skill_advance(db, character_id, body.skill_name, body.linked_attribute)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/characters/{character_id}/progression/talent", response_model=CharacterOut)
async def api_progression_talent(
    character_id: UUID,
    body: ProgressionTalent,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_character(db, user, character_id)
    try:
        return await purchase_talent(db, character_id, body.talent_name)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/characters/{character_id}/progression", response_model=ProgressionOptionsOut)
async def api_progression_options(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_character(db, user, character_id)
    try:
        opts = await get_progression_options(db, character_id)
        return ProgressionOptionsOut(
            character_id=character_id,
            xp_available=opts["xp_available"],
            skills=opts["skills"],
            talents=opts["talents"],
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/campaigns", response_model=CampaignOut)
async def api_create_campaign(
    body: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_character(db, user, body.character_id)
    try:
        c = await create_campaign(db, body.character_id)
        return _campaign_out(c)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/campaigns", response_model=list[CampaignOut])
async def api_list_campaigns(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    campaigns = await list_campaigns(db, user.id)
    result = []
    for c in campaigns:
        result.append(await _campaign_out_with_session(db, c))
    return result


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
async def api_get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    c = await get_owned_campaign(db, user, campaign_id)
    return await _campaign_out_with_session(db, c)


@router.post("/campaigns/{campaign_id}/complete", response_model=CampaignOut)
async def api_complete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_campaign(db, user, campaign_id)
    try:
        c = await mark_campaign_completed(db, campaign_id)
        return _campaign_out(c)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/campaigns/{campaign_id}/active-session", response_model=SessionOut)
async def api_campaign_active_session(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_campaign(db, user, campaign_id)
    session = await get_active_session(db, campaign_id)
    if not session:
        raise HTTPException(404, "Nenhuma sessão ativa")
    return _session_out(session)


@router.post("/campaigns/{campaign_id}/sessions", response_model=SessionOut)
async def api_start_session(
    campaign_id: UUID,
    body: SessionStart,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_campaign(db, user, campaign_id)
    try:
        s = await start_session(db, campaign_id, body.duration_minutes)
        return _session_out(s)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/sessions/{session_id}/turn", response_model=TurnResponse)
async def api_session_turn(
    session_id: UUID,
    body: PlayerAction,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    try:
        result = await gm.process_turn(db, session_id, body.action)
        from sqlalchemy import select
        from app.db.models import GameSession

        session = await db.scalar(select(GameSession).where(GameSession.id == session_id))
        return _turn_response(result, session)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/sessions/{session_id}/turn/stream")
async def api_session_turn_stream(
    session_id: UUID,
    body: PlayerAction,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    try:
        return StreamingResponse(
            gm.stream_turn(db, session_id, body.action),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


def _roll_response(result, session, character=None) -> RollResponse:
    failed = any(r.get("success") is False for r in result.roll_results)
    fortune_current = character.fortune_current if character else 0
    fortune_reroll_used = False
    if session and session.pending_roll_result:
        fortune_reroll_used = session.pending_roll_result.get("fortune_reroll_used", False)
    fortune_reroll_available = (
        failed and fortune_current > 0 and not fortune_reroll_used
    )
    return RollResponse(
        roll_results=result.roll_results,
        turn_phase=session.turn_phase if session else "awaiting_narrate",
        mode=session.mode.value if session else "EXPLORACAO",
        combat_state=session.combat_state if session else None,
        fortune_current=character.fortune_current if character else None,
        fortune_max=character.fortune_max if character else None,
        fortune_reroll_available=fortune_reroll_available,
    )


async def _session_character(db: AsyncSession, session_id: UUID):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.db.models import Campaign, GameSession

    session = await db.scalar(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(selectinload(GameSession.campaign).selectinload(Campaign.character))
    )
    character = session.campaign.character if session and session.campaign else None
    return session, character


@router.post("/sessions/{session_id}/roll", response_model=RollResponse)
async def api_session_roll(
    session_id: UUID,
    body: RollRequest = Body(default_factory=RollRequest),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    roll_override = body.roll
    try:
        result = await gm.execute_roll(db, session_id, roll_override=roll_override)
        session, character = await _session_character(db, session_id)
        return _roll_response(result, session, character)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/sessions/{session_id}/roll/fortune-reroll", response_model=RollResponse)
async def api_fortune_reroll(
    session_id: UUID,
    body: RollRequest = Body(default_factory=RollRequest),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    try:
        result = await gm.execute_fortune_reroll(db, session_id, roll_override=body.roll)
        session, character = await _session_character(db, session_id)
        return _roll_response(result, session, character)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/sessions/{session_id}/roll/narrate", response_model=TurnResponse)
async def api_session_roll_narrate(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    from sqlalchemy import select
    from app.db.models import GameSession

    try:
        result = await gm.narrate_roll(db, session_id)
        session = await db.scalar(select(GameSession).where(GameSession.id == session_id))
        return _turn_response(result, session)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/sessions/{session_id}/roll/narrate/stream")
async def api_session_roll_narrate_stream(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    try:
        return StreamingResponse(
            gm.stream_narrate_roll(db, session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/sessions/{session_id}", response_model=SessionDetailOut)
async def api_get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.db.models import Campaign, GameSession

    session = await db.scalar(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(selectinload(GameSession.campaign).selectinload(Campaign.character))
    )
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    return _session_detail(session, session.campaign)


@router.post("/sessions/{session_id}/pause", response_model=SessionDetailOut)
async def api_pause_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.db.models import Campaign, GameSession

    session = await db.scalar(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(selectinload(GameSession.campaign).selectinload(Campaign.character))
    )
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    try:
        session = await pause_session(db, session)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return _session_detail(session, session.campaign)


@router.post("/sessions/{session_id}/resume", response_model=SessionDetailOut)
async def api_resume_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.db.models import Campaign, GameSession

    session = await db.scalar(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(selectinload(GameSession.campaign).selectinload(Campaign.character))
    )
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    try:
        session = await resume_session(db, session)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return _session_detail(session, session.campaign)


@router.get("/sessions/{session_id}/history", response_model=list[SessionTurnOut])
async def api_session_history(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    from sqlalchemy import select
    from app.db.models import SessionTurn

    turns = (
        await db.scalars(
            select(SessionTurn)
            .where(SessionTurn.session_id == session_id)
            .order_by(SessionTurn.created_at)
        )
    ).all()
    return [
        SessionTurnOut(
            id=t.id,
            session_id=t.session_id,
            role=t.role,
            content=t.content,
            metadata=t.metadata_,
            created_at=t.created_at,
        )
        for t in turns
    ]


@router.post("/sessions/{session_id}/quick-roll", response_model=QuickRollResponse)
async def api_quick_roll(
    session_id: UUID,
    body: QuickRollRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_session(db, user, session_id)
    try:
        return await gm.execute_quick_roll(
            db, session_id, body.roll_type, body.key, body.modifier, roll_override=body.roll
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/campaigns/{campaign_id}/npcs", response_model=CampaignNpcListOut)
async def api_campaign_npcs(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_campaign(db, user, campaign_id)
    npcs = await list_campaign_npcs(db, campaign_id)
    return {"npcs": npcs}


@router.get("/campaigns/{campaign_id}/diary")
async def api_diary(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_campaign(db, user, campaign_id)
    from sqlalchemy import select
    from app.db.models import DiaryEntry

    entries = (
        await db.scalars(
            select(DiaryEntry)
            .where(DiaryEntry.campaign_id == campaign_id)
            .order_by(DiaryEntry.created_at)
        )
    ).all()
    return [{"id": str(e.id), "content": e.content, "created_at": e.created_at.isoformat()} for e in entries]


@router.get("/images/{job_id}/file")
async def api_image_file(job_id: UUID, db: AsyncSession = Depends(get_db)):
    from app.services.images import get_image_job, image_file_path

    job = await get_image_job(db, job_id)
    if not job:
        raise HTTPException(404, "Image job not found")
    path = image_file_path(job_id)
    if not path.is_file():
        raise HTTPException(404, "Image file not found")
    return FileResponse(path, media_type="image/jpeg")


@router.get("/images/{job_id}", response_model=ImageJobOut)
async def api_image_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    from app.services.images import get_image_job, placeholder_url

    job = await get_image_job(db, job_id)
    if not job:
        raise HTTPException(404, "Image job not found")
    return ImageJobOut(
        id=job.id,
        status=job.status,
        image_type=job.image_type,
        image_url=job.image_url,
        placeholder_url=placeholder_url(job.image_type),
    )


@router.get("/campaigns/{campaign_id}/map")
async def api_map(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_verified_user),
):
    await get_owned_campaign(db, user, campaign_id)
    from sqlalchemy import select
    from app.db.models import MapRegion

    regions = (
        await db.scalars(select(MapRegion).where(MapRegion.campaign_id == campaign_id))
    ).all()
    return [
        {"name": r.name, "description": r.description, "image_url": r.image_url, "revealed": r.revealed}
        for r in regions
    ]
