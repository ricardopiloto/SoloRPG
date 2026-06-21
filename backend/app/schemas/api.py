from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str
    background: str | None = None
    attributes: dict[str, int] = Field(default_factory=dict)
    wounds_max: int = 10
    fate_max: int = 2
    careers: list[dict] = Field(default_factory=list)
    skills: list[dict] = Field(default_factory=list)
    talents: list[dict] = Field(default_factory=list)
    trappings: list[dict] = Field(default_factory=list)


class PregenCreate(BaseModel):
    template_index: int
    name: str | None = None


class CharacterOut(BaseModel):
    id: UUID
    name: str
    status: str
    attributes: dict
    wounds_current: int
    wounds_max: int
    fate_current: int
    fate_max: int
    fortune_current: int
    fortune_max: int
    careers: list
    skills: list
    talents: list
    trappings: list
    xp_total: int
    xp_spent: int
    background: str | None

    model_config = {"from_attributes": True}


class CampaignOut(BaseModel):
    id: UUID
    character_id: UUID
    status: str
    tone: str | None
    opening_location: str | None
    world_state: str | None
    created_at: datetime
    character_name: str | None = None
    active_session_id: UUID | None = None
    active_session_paused: bool = False
    active_session_time_remaining: int | None = None

    model_config = {"from_attributes": True}


class ProgressionOptionsOut(BaseModel):
    character_id: UUID
    xp_available: int
    skills: list[dict]
    talents: list[dict]


class CampaignCreate(BaseModel):
    character_id: UUID


class SessionStart(BaseModel):
    duration_minutes: int = 45


class SessionOut(BaseModel):
    id: UUID
    campaign_id: UUID
    mode: str
    is_active: bool
    is_first_session: bool
    duration_minutes: int
    time_remaining_minutes: int
    started_at: datetime
    turn_phase: str = "normal"
    combat_state: dict | None = None
    paused_at: datetime | None = None
    images_enabled: bool = False

    model_config = {"from_attributes": True}


class PlayerAction(BaseModel):
    action: str


class RollResult(BaseModel):
    type: str
    roll: int | None = None
    target: int | None = None
    success: bool | None = None
    damage: int | None = None
    llm_text: str | None = None


class TurnResponse(BaseModel):
    narrative: str
    roll_results: list[dict] = Field(default_factory=list)
    images: list[dict] = Field(default_factory=list)
    session_ended: bool = False
    xp_awarded: int = 0
    player_summary: str | None = None
    time_remaining_minutes: int = 0
    mode: str = "EXPLORACAO"
    turn_phase: str = "normal"
    pending_test: dict | None = None
    combat_state: dict | None = None


class RollRequest(BaseModel):
    roll: int | None = None


class RollResponse(BaseModel):
    roll_results: list[dict] = Field(default_factory=list)
    turn_phase: str = "awaiting_narrate"
    mode: str = "EXPLORACAO"
    combat_state: dict | None = None
    fortune_current: int | None = None
    fortune_max: int | None = None
    fortune_reroll_available: bool = False


class ProgressionSkill(BaseModel):
    skill_name: str
    linked_attribute: str


class ProgressionTalent(BaseModel):
    talent_name: str


class QuickRollRequest(BaseModel):
    roll_type: str  # attribute | skill | weapon
    key: str
    modifier: int = 0
    roll: int | None = None


class QuickRollResponse(BaseModel):
    roll: int
    target: int
    success: bool
    levels: int
    roll_type: str
    key: str
    modifier: int
    narration_hint: str


class SessionDetailOut(SessionOut):
    campaign_id: UUID
    character_id: UUID | None = None
    character_name: str | None = None
    opening_location: str | None = None
    tone: str | None = None
    paused_at: datetime | None = None


class SessionTurnOut(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ImageJobOut(BaseModel):
    id: UUID
    status: str
    image_type: str
    image_url: str | None
    placeholder_url: str | None = None

    model_config = {"from_attributes": True}


class SkillCatalogEntry(BaseModel):
    name: str
    linked_attribute: str


class SkillCatalogOut(BaseModel):
    skills: list[SkillCatalogEntry]


class CampaignNpcOut(BaseModel):
    id: UUID
    name: str
    known_name: str | None = None
    met_location: str | None = None
    role: str | None = None
    relationship_status: str

    model_config = {"from_attributes": True}


class CampaignNpcListOut(BaseModel):
    npcs: list[CampaignNpcOut]
