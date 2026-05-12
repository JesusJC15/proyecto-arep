from fastapi import APIRouter, Depends

from app.core.errors import conflict, not_found
from app.dependencies import enforce_rate_limit, require_role
from app.dependencies import get_store
from app.repositories.base import Repository
from app.schemas.domain import AuthenticatedUser, ProfessionalCaseDetail, ProfessionalCaseSummary, UserRole


router = APIRouter()


@router.get("", response_model=list[ProfessionalCaseSummary])
def list_cases(
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(require_role(UserRole.PROFESSIONAL)),
) -> list[ProfessionalCaseSummary]:
    return store.list_escalations()


@router.get("/{case_id}", response_model=ProfessionalCaseDetail)
def get_case(
    case_id: str,
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(require_role(UserRole.PROFESSIONAL)),
) -> ProfessionalCaseDetail:
    case = store.get_professional_case(case_id)
    if case is None:
        raise not_found("Case not found")
    return case


@router.post("/{case_id}/assign", response_model=ProfessionalCaseDetail)
def assign_case(
    case_id: str,
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(require_role(UserRole.PROFESSIONAL)),
    _: None = Depends(enforce_rate_limit("mutation")),
) -> ProfessionalCaseDetail:
    current_case = store.get_professional_case(case_id)
    if current_case is None:
        raise not_found("Case not found")
    if current_case.assigned_professional_id not in {None, current_user.id}:
        raise conflict("Case is assigned to another professional")
    case = store.assign_case(case_id, current_user.id)
    if case is None:
        raise not_found("Case not found")
    store.record_audit_event(
        actor_user_id=current_user.id,
        action="professional_case.assign",
        resource_type="professional_case",
        resource_id=case_id,
        outcome="success",
    )
    return case


@router.post("/{case_id}/review", response_model=ProfessionalCaseDetail)
def review_case(
    case_id: str,
    store: Repository = Depends(get_store),
    current_user: AuthenticatedUser = Depends(require_role(UserRole.PROFESSIONAL)),
    _: None = Depends(enforce_rate_limit("mutation")),
) -> ProfessionalCaseDetail:
    current_case = store.get_professional_case(case_id)
    if current_case is None:
        raise not_found("Case not found")
    if current_case.assigned_professional_id not in {None, current_user.id}:
        raise conflict("Case is assigned to another professional")
    reviewed_case = store.review_case(case_id, current_user.id)
    if reviewed_case is None:
        raise not_found("Case not found")
    store.record_audit_event(
        actor_user_id=current_user.id,
        action="professional_case.review",
        resource_type="professional_case",
        resource_id=case_id,
        outcome="success",
    )
    return reviewed_case
