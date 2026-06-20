import pytest

from app.models import EncryptedToken
from app.services.oauth_token_service import (
    delete_tokens,
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
