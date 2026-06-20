def test_status_endpoint_works_when_disabled(client):
    resp = client.get("/api/auth/google/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["real_connectors_enabled"] is False
    assert "gmail.readonly" in " ".join(body["scopes"])
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
