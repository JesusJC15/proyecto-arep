from fastapi import APIRouter, Depends

from app.core.errors import conflict, forbidden, not_found
from app.core.tracing import trace_span
from app.dependencies import enforce_rate_limit, get_current_user, get_rag_service, require_role
from app.dependencies import get_store
from app.repositories.base import Repository
from app.schemas.domain import (
    AuthenticatedUser,
    ConsultationCreate,
    ConsultationRecord,
    Recommendation,
    UserRole,
)
from app.services.rag_service import RAGService
from app.services.triage_engine import evaluate_consultation


router = APIRouter()


@router.post("", response_model=ConsultationRecord)
def create_consultation(
    payload: ConsultationCreate,
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(require_role(UserRole.PATIENT)),
    _: None = Depends(enforce_rate_limit("mutation")),
) -> ConsultationRecord:
    consultation = store.create_consultation(payload, patient_user_id=current_user.id)
    store.record_audit_event(
        actor_user_id=current_user.id,
        action="consultation.create",
        resource_type="consultation",
        resource_id=consultation.id,
        outcome="success",
    )
    return consultation


@router.get("/{consultation_id}", response_model=ConsultationRecord)
def get_consultation(
    consultation_id: str,
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ConsultationRecord:
    consultation = store.get_consultation(consultation_id)
    if consultation is None:
        raise not_found("Consultation not found")
    if current_user.role == UserRole.PATIENT and consultation.patient_user_id != current_user.id:
        raise forbidden("Forbidden for this consultation")
    return consultation


@router.post("/{consultation_id}/triage", response_model=ConsultationRecord)
def run_triage(
    consultation_id: str,
    store: Repository = Depends(get_store),
    rag_service: RAGService = Depends(get_rag_service),
    current_user: AuthenticatedUser = Depends(require_role(UserRole.PATIENT)),
    _: None = Depends(enforce_rate_limit("mutation")),
) -> ConsultationRecord:
    consultation = store.get_consultation(consultation_id)
    if consultation is None:
        raise not_found("Consultation not found")
    if consultation.patient_user_id != current_user.id:
        raise forbidden("Forbidden for this consultation")
    with trace_span("consultation.triage", consultation_id=consultation_id, patient_user_id=current_user.id):
        triage_result, recommendation, retrieval_trace = evaluate_consultation(consultation, rag_service)
        updated = store.save_triage(consultation_id, triage_result, recommendation)
        store.record_retrieval_trace(consultation_id, retrieval_trace)
    store.record_audit_event(
        actor_user_id=current_user.id,
        action="consultation.triage",
        resource_type="consultation",
        resource_id=consultation_id,
        outcome="success",
        metadata={
            "status": updated.status.value,
            "severity": updated.triage_result.severity.value,
            "retrieval_version": retrieval_trace.retrieval_version,
            "embedding_provider": retrieval_trace.embedding_provider,
            "corpus_version": retrieval_trace.corpus_version,
        },
    )
    store.record_audit_event(
        actor_user_id=current_user.id,
        action="rag.retrieve",
        resource_type="consultation",
        resource_id=consultation_id,
        outcome="success",
        metadata={
            "query_text": retrieval_trace.query_text,
            "top_k": retrieval_trace.top_k,
            "candidates_considered": retrieval_trace.candidates_considered,
            "documents": [source.document_id for source in retrieval_trace.evidence_sources],
        },
    )
    if updated.status == updated.status.ESCALATED:
        store.record_audit_event(
            actor_user_id=current_user.id,
            action="consultation.escalated",
            resource_type="consultation",
            resource_id=consultation_id,
            outcome="success",
        )
    return updated


@router.get("/{consultation_id}/recommendation", response_model=Recommendation)
def get_recommendation(
    consultation_id: str,
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Recommendation:
    consultation = store.get_consultation(consultation_id)
    if consultation is None:
        raise not_found("Consultation not found")
    if current_user.role == UserRole.PATIENT and consultation.patient_user_id != current_user.id:
        raise forbidden("Forbidden for this consultation")
    if consultation.recommendation is None:
        raise conflict("Recommendation is not available until triage is executed")
    return consultation.recommendation
