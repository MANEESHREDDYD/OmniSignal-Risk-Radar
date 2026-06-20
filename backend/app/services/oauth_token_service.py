"""Store and retrieve OAuth tokens, always encrypted at rest.

Plaintext tokens never leave this module's call boundary: they are encrypted on
write and only decrypted for the connector that needs to call the provider. They
are never serialized to API responses or logs.
"""

from __future__ import annotations

import json
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EncryptedToken, now_iso
from .token_crypto import encrypt_token, decrypt_token


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
        existing.encrypted_access_token = enc_access
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


def delete_tokens(db: Session, oauth_connection_id: str) -> int:
    """Delete all stored tokens for a connection. Returns rows removed."""
    rows = db.scalars(
        select(EncryptedToken).where(EncryptedToken.oauth_connection_id == oauth_connection_id)
    ).all()
    for row in rows:
        db.delete(row)
    return len(rows)
