from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import forbidden, too_many_requests, unauthorized
from app.core.rate_limit import RateLimiter
from app.core.security import decode_access_token
from app.repositories.base import Repository
from app.schemas.domain import AuthenticatedUser, UserRole
from app.services.rag_service import RAGService


http_bearer = HTTPBearer(auto_error=False)


def get_store(request: Request) -> Repository:
    return request.app.state.store


def get_settings(request: Request):
    return request.app.state.settings


def get_rate_limiter(request: Request) -> RateLimiter:
    return request.app.state.rate_limiter


def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


def enforce_rate_limit(scope: str) -> Callable[[Request], None]:
    def dependency(request: Request, settings=Depends(get_settings), limiter: RateLimiter = Depends(get_rate_limiter)) -> None:
        client_host = request.client.host if request.client else "unknown"
        if scope == "auth":
            allowed = limiter.check(
                "auth",
                client_host,
                settings.auth_rate_limit_count,
                settings.auth_rate_limit_window_seconds,
            )
        else:
            allowed = limiter.check(
                f"mutation:{request.url.path}",
                client_host,
                settings.mutation_rate_limit_count,
                settings.mutation_rate_limit_window_seconds,
            )
        if not allowed:
            raise too_many_requests("Rate limit exceeded")

    return dependency


def get_current_user(
    request: Request,
    store: Repository = Depends(get_store),
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> AuthenticatedUser:
    if credentials is None:
        raise unauthorized("Missing bearer token")
    try:
        payload = decode_access_token(
            credentials.credentials,
            request.app.state.settings.jwt_secret,
            request.app.state.settings.jwt_algorithm,
        )
    except Exception as exc:
        raise unauthorized("Invalid token") from exc
    user = store.get_user(payload.sub)
    if user is None:
        raise unauthorized("Unknown user")
    return AuthenticatedUser(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
    )


def require_role(role: UserRole) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    def dependency(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role != role:
            raise forbidden("Forbidden for this role")
        return current_user

    return dependency
