"""Store and retrieve OAuth tokens, always encrypted at rest.

Plaintext tokens never leave this module's call boundary: they are encrypted on
write and only decrypted for the connector that needs to call the provider. They
are never serialized to API responses or logs.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EncryptedToken, now_iso
from .token_crypto import encrypt_token, decrypt_token


TOKEN_REFRESH_LEEWAY_SECONDS = 120


class TokenRefreshError(Exception):
    """Raised when an expired Google access token cannot be refreshed safely."""


def _uid() -> str:
    return f"tok_{uuid.uuid4().hex[:12]}"


def store_tokens(
    db: Session,
    *,
    oauth_connection_id: str,
    provider: str,
    access_token: str | None,
    refresh_token: str | None,
    token_type: str | None,
    expires_at: str | None,
    scopes: list[str],
) -> EncryptedToken:
    """Encrypt and persist tokens for a connection (replacing any existing row).

    Raises ``MissingEncryptionKeyError`` if no encryption key is configured, so
    we can never accidentally store plaintext.
    """
    existing = db.scalar(
        select(EncryptedToken).where(EncryptedToken.oauth_connection_id == oauth_connection_id)
    )
    enc_access = encrypt_token(access_token) if access_token else None
    enc_refresh = encrypt_token(refresh_token) if refresh_token else None

    if existing:
        existing.provider = provider
        if access_token is not None:
            existing.encrypted_access_token = enc_access
        if refresh_token is not None:
            existing.encrypted_refresh_token = enc_refresh
        existing.token_type = token_type
        existing.expires_at = expires_at
        existing.scopes_json = json.dumps(scopes)
        existing.updated_at = now_iso()
        return existing

    record = EncryptedToken(
        id=_uid(),
        oauth_connection_id=oauth_connection_id,
        provider=provider,
        encrypted_access_token=enc_access,
        encrypted_refresh_token=enc_refresh,
        token_type=token_type,
        expires_at=expires_at,
        scopes_json=json.dumps(scopes),
    )
    db.add(record)
    return record


def get_decrypted_tokens(db: Session, oauth_connection_id: str) -> dict | None:
    """Return decrypted tokens for internal provider calls only. Never expose."""
    db.flush()
    record = db.scalar(
        select(EncryptedToken).where(EncryptedToken.oauth_connection_id == oauth_connection_id)
    )
    if not record:
        return None
    return {
        "access_token": decrypt_token(record.encrypted_access_token) if record.encrypted_access_token else None,
        "refresh_token": decrypt_token(record.encrypted_refresh_token) if record.encrypted_refresh_token else None,
        "token_type": record.token_type,
        "expires_at": record.expires_at,
        "scopes": json.loads(record.scopes_json or "[]"),
    }


def expiry_from_seconds(
    expires_in: int | str | None, now: datetime | None = None
) -> str | None:
    if expires_in in (None, ""):
        return None
    try:
        seconds = int(expires_in)
    except (TypeError, ValueError):
        return None
    current = now or datetime.now(timezone.utc)
    return (current + timedelta(seconds=seconds)).isoformat()


def token_needs_refresh(
    expires_at: str | None,
    *,
    now: datetime | None = None,
    leeway_seconds: int = TOKEN_REFRESH_LEEWAY_SECONDS,
) -> bool:
    if not expires_at:
        return False
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    return expiry <= current + timedelta(seconds=leeway_seconds)


def get_valid_access_token(
    db: Session,
    oauth_connection_id: str,
    *,
    refresh_fn: Callable[[str], dict] | None = None,
    now: datetime | None = None,
) -> str:
    """Return a usable access token, refreshing and re-encrypting when needed."""
    tokens = get_decrypted_tokens(db, oauth_connection_id)
    if not tokens or not tokens.get("access_token"):
        raise TokenRefreshError("No stored access token is available.")
    if not token_needs_refresh(tokens.get("expires_at"), now=now):
        return tokens["access_token"]

    refresh_token = tokens.get("refresh_token")
    if not refresh_token or refresh_fn is None:
        raise TokenRefreshError("The access token expired and cannot be refreshed.")
    try:
        refreshed = refresh_fn(refresh_token)
    except Exception as exc:
        raise TokenRefreshError("Google access-token refresh failed.") from exc
    new_access_token = refreshed.get("access_token")
    if not new_access_token:
        raise TokenRefreshError("Google token refresh returned no access token.")

    expires_at = expiry_from_seconds(refreshed.get("expires_in"), now=now)
    store_tokens(
        db,
        oauth_connection_id=oauth_connection_id,
        provider="google",
        access_token=new_access_token,
        refresh_token=refreshed.get("refresh_token"),
        token_type=refreshed.get("token_type") or tokens.get("token_type"),
        expires_at=expires_at,
        scopes=refreshed.get("scope", "").split() or tokens.get("scopes", []),
    )
    db.flush()
    return new_access_token


def delete_tokens(db: Session, oauth_connection_id: str) -> int:
    """Delete all stored tokens for a connection. Returns rows removed."""
    rows = db.scalars(
        select(EncryptedToken).where(EncryptedToken.oauth_connection_id == oauth_connection_id)
    ).all()
    for row in rows:
        db.delete(row)
    return len(rows)
