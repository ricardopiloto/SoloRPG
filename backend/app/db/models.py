import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CampaignStatus(str, enum.Enum):
    ACTIVE = "ativa"
    COMPLETED = "concluida"
    UNFINISHED = "inacabada"


class SessionMode(str, enum.Enum):
    EXPLORATION = "EXPLORACAO"
    COMBAT = "COMBATE"


class CharacterStatus(str, enum.Enum):
    ALIVE = "vivo"
    DEAD = "morto"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    characters: Mapped[list["PlayerCharacter"]] = relationship(back_populates="user")
    verification_codes: Mapped[list["EmailVerificationCode"]] = relationship(back_populates="user")


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    code_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="verification_codes")


class PlayerCharacter(Base):
    __tablename__ = "player_characters"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True, index=True)
    is_starter: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[CharacterStatus] = mapped_column(Enum(CharacterStatus), default=CharacterStatus.ALIVE)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    wounds_current: Mapped[int] = mapped_column(Integer, default=0)
    wounds_max: Mapped[int] = mapped_column(Integer, default=0)
    fate_current: Mapped[int] = mapped_column(Integer, default=0)
    fate_max: Mapped[int] = mapped_column(Integer, default=0)
    fortune_current: Mapped[int] = mapped_column(Integer, default=0)
    fortune_max: Mapped[int] = mapped_column(Integer, default=0)
    careers: Mapped[list] = mapped_column(JSON, default=list)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    talents: Mapped[list] = mapped_column(JSON, default=list)
    trappings: Mapped[list] = mapped_column(JSON, default=list)
    xp_total: Mapped[int] = mapped_column(Integer, default=0)
    xp_spent: Mapped[int] = mapped_column(Integer, default=0)
    karma: Mapped[int] = mapped_column(Integer, default=0)
    social_perception: Mapped[str] = mapped_column(Text, default="desconhecido")
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="characters")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="character")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("player_characters.id"))
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.ACTIVE)
    tone: Mapped[str | None] = mapped_column(String(120), nullable=True)
    secret_objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    antagonist: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    world_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    campaign_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    narrative_phase: Mapped[str] = mapped_column(String(80), default="inicio")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    character: Mapped[PlayerCharacter] = relationship(back_populates="campaigns")
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="campaign")
    npcs: Mapped[list["NPC"]] = relationship(back_populates="campaign")
    factions: Mapped[list["Faction"]] = relationship(back_populates="campaign")
    events: Mapped[list["NarrativeEvent"]] = relationship(back_populates="campaign")
    diary_entries: Mapped[list["DiaryEntry"]] = relationship(back_populates="campaign")
    map_regions: Mapped[list["MapRegion"]] = relationship(back_populates="campaign")


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    mode: Mapped[SessionMode] = mapped_column(Enum(SessionMode), default=SessionMode.EXPLORATION)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_first_session: Mapped[bool] = mapped_column(default=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    turn_history: Mapped[list] = mapped_column(JSON, default=list)
    combat_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    pending_test: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    turn_phase: Mapped[str] = mapped_column(String(20), default="normal")
    pending_roll_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)
    player_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_paused_seconds: Mapped[int] = mapped_column(Integer, default=0)
    images_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    campaign: Mapped[Campaign] = relationship(back_populates="sessions")
    turns: Mapped[list["SessionTurn"]] = relationship(back_populates="session")


class SessionTurn(Base):
    __tablename__ = "session_turns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("game_sessions.id"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped[GameSession] = relationship(back_populates="turns")


class NPC(Base):
    __tablename__ = "npcs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    name: Mapped[str] = mapped_column(String(120))
    known_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    met_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    relationship_status: Mapped[str] = mapped_column(String(40), default="neutro")
    secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ativo")

    campaign: Mapped[Campaign] = relationship(back_populates="npcs")


class Faction(Base):
    __tablename__ = "factions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    name: Mapped[str] = mapped_column(String(120))
    reputation: Mapped[int] = mapped_column(Integer, default=0)

    campaign: Mapped[Campaign] = relationship(back_populates="factions")


class NarrativeEvent(Base):
    __tablename__ = "narrative_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("game_sessions.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    consequences: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign: Mapped[Campaign] = relationship(back_populates="events")


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("game_sessions.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign: Mapped[Campaign] = relationship(back_populates="diary_entries")


class MapRegion(Base):
    __tablename__ = "map_regions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    revealed: Mapped[bool] = mapped_column(default=True)

    campaign: Mapped[Campaign] = relationship(back_populates="map_regions")


class ImageJob(Base):
    __tablename__ = "image_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("campaigns.id"))
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("game_sessions.id"), nullable=True)
    image_type: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cache_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
