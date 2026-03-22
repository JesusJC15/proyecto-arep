from fastapi import APIRouter, HTTPException, status

from app.core.security import create_demo_token
from app.repositories.in_memory import store
from app.schemas.domain import AuthLoginRequest, AuthLoginResponse, UserSummary


router = APIRouter()


@router.post("/login", response_model=AuthLoginResponse)
def login(payload: AuthLoginRequest) -> AuthLoginResponse:
    user = store.get_user_by_credentials(payload.username, payload.password, payload.role)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username, password or role",
        )
    token = create_demo_token(user.id, user.username, user.role)
    return AuthLoginResponse(
        access_token=token,
        user=UserSummary(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
        ),
    )
