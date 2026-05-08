from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import os

import jwt

from app.schemas.domain import TokenPayload, UserRole


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, salt_hex, digest_hex = password_hash.split("$", maxsplit=2)
    if algorithm != "scrypt":
        raise ValueError("Unsupported password algorithm")
    candidate = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=2**14,
        r=8,
        p=1,
    )
    return hmac.compare_digest(candidate.hex(), digest_hex)


def create_access_token(
    user_id: str,
    username: str,
    role: UserRole,
    secret: str,
    algorithm: str,
    ttl_minutes: int,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role.value,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
        "iss": "arep-backend",
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(token: str, secret: str, algorithm: str) -> TokenPayload:
    payload = jwt.decode(token, secret, algorithms=[algorithm], issuer="arep-backend")
    return TokenPayload(
        sub=payload["sub"],
        username=payload["username"],
        role=UserRole(payload["role"]),
        iat=datetime.fromtimestamp(payload["iat"], tz=UTC),
        exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
        iss=payload["iss"],
    )
