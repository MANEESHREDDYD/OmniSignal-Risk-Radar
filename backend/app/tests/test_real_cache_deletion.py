from app.models import (
    AuditLog,
    ConnectedAccount,
    OAuthConnection,
    RawMessage,
    RealSyncedItem,
    UnifiedMessage,
    now_iso,
)
from app.services.real_ingestion_service import ingest_real_items


def _demo_message(db):
    db.add(
        ConnectedAccount(
            id="demo_acct",
            user_id="user_001",
            platform="gmail",
            account_label="Demo Gmail",
            account_identifier="demo@example.com",
            connection_status="connected",
            is_demo=True,
        )
    )
    db.add(
        RawMessage(
            id="raw_demo_1",
            connected_account_id="demo_acct",
            external_message_id="demo:1",
            platform="gmail",
            raw_payload_json="{}",
            received_at=now_iso(),
        )
    )
    db.add(
        UnifiedMessage(
            id="demo_1",
            raw_message_id="raw_demo_1",
            connected_account_id="demo_acct",
            platform="gmail",
            thread_key="demo_thread",
            sender_name="Demo",
            sender_identifier="demo@example.com",
            subject="Demo subject",
            body_text="demo body",
            sent_at=now_iso(),
            received_at=now_iso(),
        )
    )


def _real_setup(db):
    db.add(
        ConnectedAccount(
            id="real_acct",
            user_id="user_001",
            platform="google",
            account_label="Google Real",
            account_identifier="real@example.com",
            connection_status="connected",
            is_demo=False,
        )
    )
    connection = OAuthConnection(
        id="oauth_real",
        user_id="user_001",
        provider="google",
        account_email="real@example.com",
        scopes_json="[]",
        status="connected",
        connected_account_id="real_acct",
        updated_at=now_iso(),
    )
    db.add(connection)
    db.flush()
    items = [
        {
            "id": "gmail_a",
            "external_message_id": "gmail:a",
            "connected_account_id": "real_acct",
            "platform": "gmail",
            "category": "real_gmail",
            "sender_name": "Real Sender",
            "sender_identifier": "rs@example.com",
            "recipient_identifiers": [],
            "subject": "Real one",
            "body_text": "real body one",
            "thread_key": "gmail_thread_a",
            "sent_at": now_iso(),
            "received_at": now_iso(),
            "has_attachments": False,
            "is_read": True,
            "provider_resource_id": "a",
        },
        {
            "id": "gmail_b",
            "external_message_id": "gmail:b",
            "connected_account_id": "real_acct",
            "platform": "gmail",
            "category": "real_gmail",
            "sender_name": "Real Sender",
            "sender_identifier": "rs@example.com",
            "recipient_identifiers": [],
            "subject": "Real two",
            "body_text": "real body two",
            "thread_key": "gmail_thread_b",
            "sent_at": now_iso(),
            "received_at": now_iso(),
            "has_attachments": False,
            "is_read": True,
            "provider_resource_id": "b",
        },
    ]
    counts = ingest_real_items(db, connection=connection, connected_account_id="real_acct", items=items)
    return connection, counts


def test_ingest_then_delete_cache_removes_only_real(client, db, monkeypatch, token_key):
    monkeypatch.setenv("REAL_CONNECTORS_ENABLED", "true")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")

    _demo_message(db)
    connection, counts = _real_setup(db)
    db.commit()

    assert counts["created"] == 2
    assert db.query(RealSyncedItem).count() == 2
    assert db.get(UnifiedMessage, "gmail_a") is not None
    assert db.get(UnifiedMessage, "demo_1") is not None

    resp = client.post(f"/api/auth/google/delete-cache/{connection.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "cache_deleted"
    assert body["messages_deleted"] == 2

    # Real data gone; demo data preserved.
    assert db.get(UnifiedMessage, "gmail_a") is None
    assert db.get(UnifiedMessage, "gmail_b") is None
    assert db.query(RealSyncedItem).count() == 0
    assert db.get(UnifiedMessage, "demo_1") is not None
    assert db.get(ConnectedAccount, "demo_acct") is not None

    # Audit log written for the deletion.
    audits = db.query(AuditLog).filter(AuditLog.action == "Deleted local real cache").all()
    assert len(audits) == 1
