from app.models import RealSyncRun


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
