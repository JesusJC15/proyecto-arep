from __future__ import annotations

from typing import Protocol

from app.schemas.domain import (
    AuditEvent,
    CorpusChunkRecord,
    CorpusDocumentRecord,
    ConsultationCreate,
    ConsultationRecord,
    ProfessionalCaseDetail,
    ProfessionalCaseSummary,
    RAGStatus,
    Recommendation,
    RetrievalTrace,
    TriageResult,
    UserRecord,
    UserRole,
)


class Repository(Protocol):
    def initialize(self, seed_demo_data: bool) -> None: ...
    def healthcheck(self) -> None: ...
    def dispose(self) -> None: ...
    def get_user(self, user_id: str) -> UserRecord | None: ...
    def get_user_by_credentials(self, username: str, password: str, role: UserRole) -> UserRecord | None: ...
    def create_consultation(self, payload: ConsultationCreate, patient_user_id: str) -> ConsultationRecord: ...
    def get_consultation(self, consultation_id: str) -> ConsultationRecord | None: ...
    def save_triage(
        self,
        consultation_id: str,
        triage_result: TriageResult,
        recommendation: Recommendation,
    ) -> ConsultationRecord: ...
    def list_escalations(self) -> list[ProfessionalCaseSummary]: ...
    def get_professional_case(self, case_id: str) -> ProfessionalCaseDetail | None: ...
    def assign_case(self, case_id: str, professional_id: str) -> ProfessionalCaseDetail | None: ...
    def review_case(self, case_id: str, professional_id: str) -> ProfessionalCaseDetail | None: ...
    def replace_corpus(
        self,
        documents: list[CorpusDocumentRecord],
        chunks: list[CorpusChunkRecord],
        index_version: str,
        index_artifact_path: str,
        embedding_provider: str,
        embedding_model: str,
        corpus_version: str,
    ) -> RAGStatus: ...
    def get_rag_status(self) -> RAGStatus | None: ...
    def record_retrieval_trace(
        self,
        consultation_id: str | None,
        trace: RetrievalTrace,
    ) -> None: ...
    def record_audit_event(
        self,
        actor_user_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None,
        outcome: str,
        metadata: dict[str, object] | None = None,
    ) -> AuditEvent: ...
    def list_audit_events(self) -> list[AuditEvent]: ...
