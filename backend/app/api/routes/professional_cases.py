from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import require_role
from app.repositories.in_memory import store
from app.schemas.domain import DemoUser, ProfessionalCaseSummary, UserRole


router = APIRouter()


@router.get("", response_model=list[ProfessionalCaseSummary])
def list_cases(
    current_user: DemoUser = Depends(require_role(UserRole.PROFESSIONAL)),
) -> list[ProfessionalCaseSummary]:
    cases = store.list_escalations()
    return [
        ProfessionalCaseSummary(
            id=case.id,
            consultation_id=case.consultation_id,
            severity=case.triage_result.severity,
            review_status=case.review_status,
            reason=case.reason,
            created_at=case.created_at,
        )
        for case in cases
    ]


@router.get("/{case_id}")
def get_case(
    case_id: str,
    current_user: DemoUser = Depends(require_role(UserRole.PROFESSIONAL)),
) -> dict:
    case = store.get_escalation(case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return {
        "id": case.id,
        "consultation_id": case.consultation_id,
        "assigned_professional_id": current_user.id,
        "review_status": case.review_status,
        "reason": case.reason,
        "created_at": case.created_at,
        "triage_result": case.triage_result,
        "recommendation": case.recommendation,
    }
