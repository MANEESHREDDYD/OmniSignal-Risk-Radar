from datetime import datetime, timedelta, timezone

from app.config import settings
from app.models import EncryptedToken
from app.routers import auth_google
from app.services.oauth_token_service import get_decrypted_tokens


def test_status_endpoint_works_when_disabled(client):
    resp = client.get("/api/auth/google/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["real_connectors_enabled"] is False
    assert "gmail.readonly" in " ".join(body["scopes"])
    assert "calendar.calendarlist.readonly" not in " ".join(body["scopes"])
    # Status must not leak secrets.
    assert "client_secret" not in body
    assert "GOOGLE_CLIENT_SECRET" not in resp.text


def test_oauth_start_blocked_when_disabled(client):
    resp = client.get("/api/auth/google/start")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "blocked_disabled"
    assert "authorization_url" not in body


def test_oauth_start_blocked_missing_config_when_enabled(client, monkeypatch):
    monkeypatch.setenv("REAL_CONNECTORS_ENABLED", "true")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    resp = client.get("/api/auth/google/start")
    body = resp.json()
    assert body["status"] == "blocked_missing_config"


def test_oauth_start_returns_url_when_fully_configured(client, monkeypatch, token_key):
    monkeypatch.setenv("REAL_CONNECTORS_ENABLED", "true")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    resp = client.get("/api/auth/google/start")
    body = resp.json()
    assert "authorization_url" in body
    assert "accounts.google.com" in body["authorization_url"]
    assert "gmail.readonly" in body["authorization_url"]
    # The client secret must never appear in the authorization URL.
    assert "test-secret" not in body["authorization_url"]


def test_oauth_state_valid_missing_unknown_and_expired():
    auth_google._pending_states.clear()
    now = datetime(2026, 6, 20, tzinfo=timezone.utc)
    state = auth_google._create_oauth_state(now=now)
    assert auth_google._consume_oauth_state(
        state, now=now + timedelta(minutes=1)
    ) == "valid"
    assert auth_google._consume_oauth_state("", now=now) == "missing"
    assert auth_google._consume_oauth_state("not-known", now=now) == "unknown"
    expired = auth_google._create_oauth_state(now=now)
    assert auth_google._consume_oauth_state(
        expired, now=now + timedelta(minutes=11)
    ) == "expired"


def test_multiple_oauth_states_can_be_valid_during_local_development():
    auth_google._pending_states.clear()
    now = datetime(2026, 6, 20, tzinfo=timezone.utc)
    first = auth_google._create_oauth_state(now=now)
    second = auth_google._create_oauth_state(now=now)
    assert first != second
    assert auth_google._consume_oauth_state(first, now=now) == "valid"
    assert auth_google._consume_oauth_state(second, now=now) == "valid"


def test_default_settings_remain_safe(monkeypatch):
    for name in [
        "DEMO_MODE",
        "REAL_CONNECTORS_ENABLED",
        "APPROVAL_GATED_WRITES",
    ]:
        monkeypatch.delenv(name, raising=False)
    assert settings.DEMO_MODE is True
    assert settings.REAL_CONNECTORS_ENABLED is False
    assert settings.APPROVAL_GATED_WRITES is False


def test_callback_stores_expiry_from_google_payload(
    client, db, monkeypatch, token_key
):
    monkeypatch.setenv("REAL_CONNECTORS_ENABLED", "true")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(
        auth_google.google_oauth,
        "exchange_code",
        lambda _code: {
            "access_token": "callback-access",
            "refresh_token": "callback-refresh",
            "token_type": "Bearer",
            "expires_in": 3600,
        },
    )
    monkeypatch.setattr(
        auth_google.google_oauth,
        "fetch_userinfo",
        lambda _token: {
            "email": "oauth-user@example.test",
            "name": "OAuth User",
        },
    )
    auth_google._pending_states.clear()
    state = client.get("/api/auth/google/start").json()["state"]
    response = client.get(
        f"/api/auth/google/callback?code=mock-code&state={state}",
        follow_redirects=False,
    )
    assert response.status_code in {302, 307}
    row = db.query(EncryptedToken).one()
    assert row.expires_at is not None
    assert datetime.fromisoformat(row.expires_at) > datetime.now(timezone.utc)
    tokens = get_decrypted_tokens(db, row.oauth_connection_id)
    assert tokens["access_token"] == "callback-access"
