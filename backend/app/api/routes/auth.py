from fastapi import APIRouter, Depends

from app.core.errors import unauthorized
from app.core.logging import log_event
from app.core.security import create_access_token
from app.dependencies import enforce_rate_limit, get_current_user, get_settings, get_store
from app.repositories.base import Repository
from app.schemas.domain import AuthLoginRequest, AuthLoginResponse, AuthenticatedUser, UserSummary


router = APIRouter()


@router.post("/login", response_model=AuthLoginResponse)
def login(
    payload: AuthLoginRequest,
    store: Repository = Depends(get_store),
    settings=Depends(get_settings),
    _: None = Depends(enforce_rate_limit("auth")),
) -> AuthLoginResponse:
    user = store.get_user_by_credentials(payload.username, payload.password, payload.role)
    if user is None:
        store.record_audit_event(
            actor_user_id=None,
            action="auth.login",
            resource_type="user",
            resource_id=payload.username,
            outcome="failure",
            metadata={"role": payload.role.value},
        )
        raise unauthorized("Invalid username, password or role")
    token = create_access_token(
        user.id,
        user.username,
        user.role,
        settings.jwt_secret,
        settings.jwt_algorithm,
        settings.access_token_ttl_minutes,
    )
    store.record_audit_event(
        actor_user_id=user.id,
        action="auth.login",
        resource_type="user",
        resource_id=user.id,
        outcome="success",
        metadata={"role": user.role.value},
    )
    log_event("auth.login", actor_user_id=user.id, role=user.role.value, outcome="success")
    return AuthLoginResponse(
        access_token=token,
        user=UserSummary(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
        ),
    )


@router.get("/session", response_model=UserSummary)
def read_session(current_user: AuthenticatedUser = Depends(get_current_user)) -> UserSummary:
    return UserSummary(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
    )
