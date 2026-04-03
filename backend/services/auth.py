from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.services.repositories import fetch_one

security = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user_id: str
    org_id: str
    role: str


@dataclass
class APIKeyRecord:
    api_key: str
    key_prefix: str
    key_hash: str


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_api_key_record() -> APIKeyRecord:
    token = secrets.token_urlsafe(32)
    api_key = f"pk_live_{token}"
    return APIKeyRecord(api_key=api_key, key_prefix=api_key[:18], key_hash=_hash_key(api_key))


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> AuthContext:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = credentials.credentials
    if not token.startswith("pk_live_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    row = fetch_one(
        "SELECT id, org_id, role, api_key_hash FROM users WHERE api_key_prefix = ?",
        (token[:18],),
    )
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not hmac.compare_digest(row["api_key_hash"], _hash_key(token)):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AuthContext(user_id=row["id"], org_id=row["org_id"], role=row["role"])


def require_roles(*allowed_roles: str):
    def dependency(ctx: AuthContext = Depends(require_auth)) -> AuthContext:
        if ctx.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return ctx

    return dependency
