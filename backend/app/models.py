from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OpportunityMode(str, enum.Enum):
    online = "online"
    offline = "offline"


class OpportunityCategory(str, enum.Enum):
    job = "job"
    course = "course"
    volunteer = "volunteer"
    internship = "internship"
    scholarship = "scholarship"


class OpportunityType(str, enum.Enum):
    paid = "paid"
    free = "free"
    volunteer = "volunteer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    locale: Mapped[str] = mapped_column(String(16), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ScamIndicator(Base):
    __tablename__ = "scam_indicators"
    __table_args__ = (UniqueConstraint("pattern", "category", "source", name="uq_indicator_pattern_cat_src"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="", nullable=False)
    source: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ar: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    description_en: Mapped[str] = mapped_column(Text, default="", nullable=False)
    description_ar: Mapped[str] = mapped_column(Text, default="", nullable=False)
    organization: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    position: Mapped[str] = mapped_column(String(255), default="", nullable=False, index=True)
    governorate: Mapped[str] = mapped_column(String(64), default="", nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    category: Mapped[str] = mapped_column(String(32), default="job", nullable=False, index=True)
    mode: Mapped[OpportunityMode] = mapped_column(Enum(OpportunityMode), nullable=False)
    opportunity_type: Mapped[OpportunityType] = mapped_column(Enum(OpportunityType), nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_volunteer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_age: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_classified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), default="", nullable=False)
    fallback_url: Mapped[str] = mapped_column(String(2048), default="", nullable=False)
    deadline: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    creator = relationship("User")
