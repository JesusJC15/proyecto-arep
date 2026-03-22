from __future__ import annotations

import base64
import json

from app.schemas.domain import UserRole


def _b64encode(value: dict[str, str]) -> str:
    raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64decode(value: str) -> dict[str, str]:
    padding = "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode(f"{value}{padding}".encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def create_demo_token(user_id: str, username: str, role: UserRole) -> str:
    header = _b64encode({"alg": "none", "typ": "JWT"})
    payload = _b64encode({"sub": user_id, "username": username, "role": role.value})
    return f"{header}.{payload}."


def decode_demo_token(token: str) -> dict[str, str]:
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("Malformed token")
    return _b64decode(parts[1])
