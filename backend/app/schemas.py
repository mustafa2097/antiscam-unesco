from __future__ import annotations

from enum import Enum
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.config import get_settings
from app.models import OpportunityCategory, OpportunityMode, OpportunityType
from app.security import sanitize_text


class ScanResultPayload(BaseModel):
    risk_score: float | None = None
    risk_level: str | None = None
    matched_indicators: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TextScanRequest(BaseModel):
    content: str = Field(..., min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        settings = get_settings()
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("content must not be empty")
        if len(cleaned) > settings.max_text_length:
            raise ValueError("content exceeds max length")
        return cleaned


class LinkScanRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        parsed = urlparse(cleaned)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("url scheme must be http or https")
        if not parsed.netloc:
            raise ValueError("url must include a valid host")
        if parsed.username or parsed.password:
            raise ValueError("url must not include credentials")
        return cleaned


class IngestFormat(str, Enum):
    json = "json"
    csv = "csv"


class IndicatorRow(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=500)
    category: str = Field(..., min_length=1, max_length=100)
    severity: float = Field(..., ge=0.0, le=1.0)
    language: str = Field(default="", max_length=16)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("pattern", "category", "language")
    @classmethod
    def clean_fields(cls, value: str) -> str:
        return sanitize_text(value)


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=120)
    password: str = Field(..., min_length=10, max_length=128)
    locale: str = Field(default="", max_length=16)

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if len(cleaned) < 2:
            raise ValueError("full_name too short")
        return cleaned

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if len(value) < 10:
            raise ValueError("password too short")
        if value.lower() == value or value.upper() == value:
            raise ValueError("password must mix letter cases")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("password must include a digit")
        if not any(ch in "!@#$%^&*()-_=+[]{};:,.?/" for ch in value):
            raise ValueError("password must include a symbol")
        return value

    @field_validator("locale")
    @classmethod
    def clean_locale(cls, value: str) -> str:
        return sanitize_text(value) if value else ""


class UserPublic(BaseModel):
    id: UUID
    email: str  # str (not EmailStr) so local-dev addresses like *.local validate
    full_name: str = ""
    locale: str = ""

    model_config = {"from_attributes": True}


class OpportunityFilter(str, Enum):
    job_online = "job_online"
    job_onsite = "job_onsite"
    course_paid = "course_paid"
    course_free = "course_free"
    volunteer = "volunteer"


class OpportunityPublic(BaseModel):
    id: UUID
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    organization: str
    position: str = ""
    governorate: str = ""
    city: str
    category: str
    mode: OpportunityMode
    opportunity_type: OpportunityType
    is_free: bool
    is_volunteer: bool
    min_age: int
    verified: bool
    ai_classified: bool = False
    source_url: str
    fallback_url: str = ""
    deadline: str = ""

    model_config = {"from_attributes": True, "use_enum_values": True}


class OpportunityCategoryQuery(str, Enum):
    job = "job"
    course = "course"
    volunteer = "volunteer"
    internship = "internship"
    scholarship = "scholarship"


class OpportunitySubFilter(str, Enum):
    online = "online"
    onsite = "onsite"
    paid = "paid"
    free = "free"
