from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    PATIENT = "patient"
    PROFESSIONAL = "professional"


class ConsultationStatus(str, Enum):
    SUBMITTED = "submitted"
    TRIAGED = "triaged"
    RECOMMENDED = "recommended"
    ESCALATED = "escalated"
    REVIEWED = "reviewed"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DemoUser(BaseModel):
    id: str
    username: str
    full_name: str
    password: str
    role: UserRole


class AuthLoginRequest(BaseModel):
    username: str
    password: str
    role: UserRole


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserSummary"


class UserSummary(BaseModel):
    id: str
    username: str
    full_name: str
    role: UserRole


class SymptomEntryInput(BaseModel):
    symptom: str
    duration: str
    intensity: Literal["low", "medium", "high"]
    notes: str | None = None


class ConsultationCreate(BaseModel):
    chief_complaint: str = Field(..., min_length=4)
    context_notes: str = ""
    age_range: str = "adult"
    chronic_conditions: list[str] = Field(default_factory=list)
    symptoms: list[SymptomEntryInput] = Field(..., min_length=1)


class SymptomEntry(BaseModel):
    id: str
    symptom: str
    duration: str
    intensity: str
    notes: str | None = None


class TriageResult(BaseModel):
    severity: SeverityLevel
    decision: Literal["self_care", "watch_and_wait", "professional_review"]
    rationale: str
    confidence: float
    prompt_version: str


class EvidenceSource(BaseModel):
    id: str
    title: str
    source_type: str
    uri: str
    snippet: str


class Recommendation(BaseModel):
    summary: str
    disclaimer: str
    evidence_sources: list[EvidenceSource]
    generated_at: datetime


class ConsultationRecord(BaseModel):
    id: str
    patient_user_id: str
    chief_complaint: str
    context_notes: str
    age_range: str
    chronic_conditions: list[str]
    symptoms: list[SymptomEntry]
    status: ConsultationStatus
    created_at: datetime
    triage_result: TriageResult | None = None
    recommendation: Recommendation | None = None


class EscalationCase(BaseModel):
    id: str
    consultation_id: str
    assigned_professional_id: str | None = None
    review_status: Literal["pending", "reviewed"] = "pending"
    reason: str
    created_at: datetime
    triage_result: TriageResult
    recommendation: Recommendation


class ProfessionalCaseSummary(BaseModel):
    id: str
    consultation_id: str
    severity: SeverityLevel
    review_status: Literal["pending", "reviewed"]
    reason: str
    created_at: datetime


UserSummary.model_rebuild()
AuthLoginResponse.model_rebuild()
