from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator


class CharacterCreate(BaseModel):
    """Legacy free-form create — rejected unless using creation draft."""

    name: str
    background: str | None = None
    attributes: dict[str, int] = Field(default_factory=dict)
    wounds_max: int = 10
    fate_max: int = 2
    careers: list[dict] = Field(default_factory=list)
    skills: list[dict] = Field(default_factory=list)
    talents: list[dict] = Field(default_factory=list)
    trappings: list[dict] = Field(default_factory=list)


class CharacterCreationDraft(BaseModel):
    step: str | None = None
    species_id: str = "human"
    species_method: str = "choose"
    career_id: str | None = None
    career_method: str = "choose"
    career_roll_count: int = 0
    career_roll_options: list[str] = Field(default_factory=list)
    attributes_method: str = "roll"
    attribute_rolls: dict[str, int] = Field(default_factory=dict)
    attribute_allocated: dict[str, int] = Field(default_factory=dict)
    attribute_advances: dict[str, int] = Field(default_factory=dict)
    attributes_swapped: bool = False
    attributes_rerolled: bool = False
    fate_allotted: int = 2
    species_skills: dict[str, int] = Field(default_factory=dict)
    career_skills: dict[str, int] = Field(default_factory=dict)
    career_talent: str | None = None
    species_talents: list[str] = Field(default_factory=list)
    name: str = ""
    background: str | None = None


class CharacterCreationValidateOut(BaseModel):
    valid: bool
    errors: list[dict[str, str]]
    computed: dict | None = None


class CharacterCreationSubmit(BaseModel):
    draft: CharacterCreationDraft


class BackgroundGenerateRequest(BaseModel):
    name: str
    career: str
    species: str = "Humano"
    talents: list[str] = Field(default_factory=list)
    skills_summary: str | None = None
    trappings: list[str] = Field(default_factory=list)
    hints: str | None = None


class BackgroundGenerateOut(BaseModel):
    background: str


class CareerSummaryOut(BaseModel):
    id: str
    name: str
    career_group: str
    career_class: str = Field(alias="class")
    tier: int = 1

    model_config = {"populate_by_name": True}


class CareerDetailOut(CareerSummaryOut):
    skills: list[str]
    talents: list[str]
    trappings: list[dict]


class CareerListOut(BaseModel):
    careers: list[CareerSummaryOut]


class CreationOptionsOut(BaseModel):
    options: dict


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
    progression_window_active: bool = False
    refund_budget_remaining: int = 0
    refund_budget_total: int = 0
    refundable_purchases: list["ProgressionPurchaseOut"] = Field(default_factory=list)


class ProgressionPurchaseOut(BaseModel):
    id: UUID
    type: str
    skill_name: str | None = None
    linked_attribute: str | None = None
    talent_name: str | None = None
    cost: int
    refundable_xp: int
    refunded: bool = False


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
    scene_mood: str | None = None


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


class ProgressionRefundIn(BaseModel):
    purchase_id: UUID


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


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Senhas não conferem")
        return self


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=320)
    password: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=8, max_length=8, pattern=r"^\d{8}$")


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    id: UUID
    email: str
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterOut(BaseModel):
    user_id: UUID
    email: str
    verification_required: bool = True


class AuthTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    starter_character: CharacterOut | None = None


class AuthConfigOut(BaseModel):
    auth_mode: str
    login_username: str
    registration_enabled: bool
