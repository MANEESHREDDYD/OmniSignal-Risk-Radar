from datetime import datetime, timedelta, timezone

from app.models import (
    ConnectedAccount,
    OAuthConnection,
    RealSyncRun,
    now_iso,
)
from app.routers import real_sync
from app.services.oauth_token_service import store_tokens


def test_gmail_sync_blocked_when_disabled(client, db):
    resp = client.post("/api/real-sync/google/oauth_x/gmail")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "blocked_disabled"
    # A blocked run is recorded for auditability.
    run = db.query(RealSyncRun).filter_by(id=body["sync_run_id"]).one()
    assert run.status == "blocked_disabled"
    assert run.sync_type == "gmail_messages"


def test_calendar_sync_blocked_when_disabled(client):
    resp = client.post("/api/real-sync/google/oauth_x/calendar")
    assert resp.json()["status"] == "blocked_disabled"


def test_full_sync_blocked_when_disabled(client):
    resp = client.post("/api/real-sync/google/oauth_x/full-readonly")
    assert resp.json()["status"] == "blocked_disabled"


def test_runs_listing_is_available_when_disabled(client):
    resp = client.get("/api/real-sync/runs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_sync_blocked_missing_config_when_enabled(client, monkeypatch):
    monkeypatch.setenv("REAL_CONNECTORS_ENABLED", "true")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    resp = client.post("/api/real-sync/google/oauth_x/gmail")
    assert resp.json()["status"] == "blocked_missing_config"


def test_expired_token_refresh_failure_marks_connection_error(
    client, db, monkeypatch, token_key
):
    monkeypatch.setenv("REAL_CONNECTORS_ENABLED", "true")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
    db.add(
        ConnectedAccount(
            id="acct_refresh_failure",
            user_id="user_001",
            platform="google",
            account_label="Google",
            account_identifier="failure@example.test",
            connection_status="connected",
            is_demo=False,
        )
    )
    connection = OAuthConnection(
        id="oauth_refresh_failure",
        user_id="user_001",
        provider="google",
        account_email="failure@example.test",
        scopes_json="[]",
        status="connected",
        connected_account_id="acct_refresh_failure",
        updated_at=now_iso(),
    )
    db.add(connection)
    store_tokens(
        db,
        oauth_connection_id=connection.id,
        provider="google",
        access_token="expired",
        refresh_token="refresh",
        token_type="Bearer",
        expires_at=(
            datetime.now(timezone.utc) - timedelta(minutes=1)
        ).isoformat(),
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    db.commit()

    def fail(_refresh_token):
        raise RuntimeError("mock refresh failure")

    monkeypatch.setattr(
        real_sync.google_oauth, "refresh_access_token", fail
    )
    response = client.post(
        f"/api/real-sync/google/{connection.id}/gmail"
    )
    assert response.json()["status"] == "failed"
    db.refresh(connection)
    assert connection.status == "error"
    run = db.query(RealSyncRun).filter_by(
        oauth_connection_id=connection.id
    ).one()
    assert run.status == "failed"
    assert run.error_message == "TokenRefreshError"
