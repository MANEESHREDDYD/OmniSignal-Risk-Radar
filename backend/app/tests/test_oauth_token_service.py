import pytest
from datetime import datetime, timedelta, timezone

from app.models import EncryptedToken
from app.services.oauth_token_service import (
    TokenRefreshError,
    delete_tokens,
    get_valid_access_token,
    get_decrypted_tokens,
    store_tokens,
)
from app.services.token_crypto import MissingEncryptionKeyError


def _store(db):
    return store_tokens(
        db,
        oauth_connection_id="oauth_1",
        provider="google",
        access_token="access-123",
        refresh_token="refresh-456",
        token_type="Bearer",
        expires_at=None,
        scopes=["gmail.readonly"],
    )


def test_store_encrypts_and_does_not_persist_plaintext(db, token_key):
    _store(db)
    db.flush()
    row = db.query(EncryptedToken).one()
    assert row.encrypted_access_token != "access-123"
    assert row.encrypted_refresh_token != "refresh-456"
    assert "access-123" not in (row.encrypted_access_token or "")


def test_get_decrypted_returns_original(db, token_key):
    _store(db)
    db.flush()
    tokens = get_decrypted_tokens(db, "oauth_1")
    assert tokens["access_token"] == "access-123"
    assert tokens["refresh_token"] == "refresh-456"


def test_disconnect_deletes_tokens(db, token_key):
    _store(db)
    db.flush()
    removed = delete_tokens(db, "oauth_1")
    db.flush()
    assert removed == 1
    assert get_decrypted_tokens(db, "oauth_1") is None


def test_missing_key_blocks_token_storage(db, monkeypatch):
    monkeypatch.delenv("TOKEN_ENCRYPTION_KEY", raising=False)
    with pytest.raises(MissingEncryptionKeyError):
        _store(db)


def test_valid_access_token_does_not_refresh(db, token_key):
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    store_tokens(
        db,
        oauth_connection_id="oauth_valid",
        provider="google",
        access_token="still-valid",
        refresh_token="refresh-valid",
        token_type="Bearer",
        expires_at=expires_at,
        scopes=["gmail.readonly"],
    )
    called = False

    def refresh(_token):
        nonlocal called
        called = True
        return {}

    assert get_valid_access_token(
        db, "oauth_valid", refresh_fn=refresh
    ) == "still-valid"
    assert called is False


def test_expired_access_token_refreshes_and_reencrypts(db, token_key):
    now = datetime(2026, 6, 20, tzinfo=timezone.utc)
    store_tokens(
        db,
        oauth_connection_id="oauth_expired",
        provider="google",
        access_token="expired-access",
        refresh_token="refresh-secret",
        token_type="Bearer",
        expires_at=(now - timedelta(minutes=1)).isoformat(),
        scopes=["gmail.readonly"],
    )

    access = get_valid_access_token(
        db,
        "oauth_expired",
        now=now,
        refresh_fn=lambda refresh: {
            "access_token": "fresh-access",
            "expires_in": 3600,
            "token_type": "Bearer",
        },
    )
    assert access == "fresh-access"
    row = db.query(EncryptedToken).filter_by(
        oauth_connection_id="oauth_expired"
    ).one()
    assert row.encrypted_access_token != "fresh-access"
    tokens = get_decrypted_tokens(db, "oauth_expired")
    assert tokens["access_token"] == "fresh-access"
    assert tokens["refresh_token"] == "refresh-secret"
    assert tokens["expires_at"] == (now + timedelta(hours=1)).isoformat()


def test_expired_access_token_refresh_failure(db, token_key):
    now = datetime(2026, 6, 20, tzinfo=timezone.utc)
    store_tokens(
        db,
        oauth_connection_id="oauth_failed",
        provider="google",
        access_token="expired-access",
        refresh_token="refresh-secret",
        token_type="Bearer",
        expires_at=(now - timedelta(minutes=1)).isoformat(),
        scopes=["gmail.readonly"],
    )

    def fail(_refresh):
        raise RuntimeError("provider unavailable")

    with pytest.raises(TokenRefreshError):
        get_valid_access_token(
            db, "oauth_failed", now=now, refresh_fn=fail
        )
