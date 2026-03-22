from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, require_role
from app.repositories.in_memory import store
from app.schemas.domain import (
    ConsultationCreate,
    ConsultationRecord,
    DemoUser,
    Recommendation,
    UserRole,
)
from app.services.triage_engine import evaluate_consultation


router = APIRouter()


@router.post("", response_model=ConsultationRecord)
def create_consultation(
    payload: ConsultationCreate,
    current_user: DemoUser = Depends(require_role(UserRole.PATIENT)),
) -> ConsultationRecord:
    return store.create_consultation(payload, patient_user_id=current_user.id)


@router.get("/{consultation_id}", response_model=ConsultationRecord)
def get_consultation(
    consultation_id: str,
    current_user: DemoUser = Depends(get_current_user),
) -> ConsultationRecord:
    consultation = store.get_consultation(consultation_id)
    if consultation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    if current_user.role == UserRole.PATIENT and consultation.patient_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this consultation")
    return consultation


@router.post("/{consultation_id}/triage", response_model=ConsultationRecord)
def run_triage(
    consultation_id: str,
    current_user: DemoUser = Depends(require_role(UserRole.PATIENT)),
) -> ConsultationRecord:
    consultation = store.get_consultation(consultation_id)
    if consultation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    if consultation.patient_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this consultation")
    triage_result, recommendation = evaluate_consultation(consultation)
    return store.save_triage(consultation_id, triage_result, recommendation)


@router.get("/{consultation_id}/recommendation", response_model=Recommendation)
def get_recommendation(
    consultation_id: str,
    current_user: DemoUser = Depends(get_current_user),
) -> Recommendation:
    consultation = store.get_consultation(consultation_id)
    if consultation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    if current_user.role == UserRole.PATIENT and consultation.patient_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this consultation")
    if consultation.recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recommendation is not available until triage is executed",
        )
    return consultation.recommendation
