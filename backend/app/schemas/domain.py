from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    PATIENT = "patient"
    PROFESSIONAL = "professional"


class ConsultationStatus(str, Enum):
    SUBMITTED = "submitted"
    RECOMMENDED = "recommended"
    ESCALATED = "escalated"
    REVIEWED = "reviewed"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserRecord(BaseModel):
    id: str
    username: str
    full_name: str
    password_hash: str
    role: UserRole


class AuthenticatedUser(BaseModel):
    id: str
    username: str
    full_name: str
    role: UserRole


class AuthLoginRequest(BaseModel):
    username: str
    password: str
    role: UserRole


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserSummary"


class TokenPayload(BaseModel):
    sub: str
    username: str
    role: UserRole
    iat: datetime
    exp: datetime
    iss: str


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
    document_id: str
    chunk_id: str
    title: str
    source_type: str
    uri: str
    snippet: str
    retrieval_score: float
    rank: int
    retrieval_method: str
    match_rationale: str
    matched_terms: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    summary: str
    disclaimer: str
    evidence_sources: list[EvidenceSource]
    generated_at: datetime
    retrieval_version: str
    embedding_provider: str
    embedding_model: str
    corpus_version: str


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
    review_status: Literal["pending", "assigned", "reviewed"] = "pending"
    reason: str
    created_at: datetime
    reviewed_at: datetime | None = None
    triage_result: TriageResult
    recommendation: Recommendation


class ProfessionalCaseSummary(BaseModel):
    id: str
    consultation_id: str
    severity: SeverityLevel
    review_status: Literal["pending", "assigned", "reviewed"]
    reason: str
    created_at: datetime


class ProfessionalCaseDetail(BaseModel):
    id: str
    consultation_id: str
    assigned_professional_id: str | None = None
    review_status: Literal["pending", "assigned", "reviewed"]
    reason: str
    created_at: datetime
    reviewed_at: datetime | None = None
    triage_result: TriageResult
    recommendation: Recommendation
    consultation: ConsultationRecord


class AuditEvent(BaseModel):
    id: str
    actor_user_id: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    outcome: str
    metadata: dict[str, Any] | None = None
    created_at: datetime


class CorpusDocumentRecord(BaseModel):
    document_id: str
    title: str
    source_type: str
    source_uri: str
    clinical_topic: str
    audience: str
    publication_or_revision_date: str
    curation_status: str
    language: str
    license_or_usage_note: str
    summary: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CorpusChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    title: str
    content: str
    token_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalTrace(BaseModel):
    query_text: str
    query_terms: list[str]
    retrieval_version: str
    embedding_provider: str
    embedding_model: str
    corpus_version: str
    index_version: str
    top_k: int
    candidates_considered: int
    evidence_sources: list[EvidenceSource]


class RAGStatus(BaseModel):
    corpus_version: str
    retrieval_version: str
    embedding_provider: str
    embedding_model: str
    documents: int
    chunks: int
    index_version: str
    index_artifact_path: str


UserSummary.model_rebuild()
AuthLoginResponse.model_rebuild()
