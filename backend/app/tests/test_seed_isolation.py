from sqlalchemy import func, select

from app.models import (
    ConnectedAccount,
    EncryptedToken,
    OAuthConnection,
    ProviderMessageCursor,
    RawMessage,
    RealSyncedItem,
    RealSyncRun,
    UnifiedMessage,
    now_iso,
)
from app.seed import seed_database


def _add_real_state(db):
    db.add(
        ConnectedAccount(
            id="acct_real_preserved",
            user_id="user_001",
            platform="google",
            account_label="Real Google",
            account_identifier="real@example.test",
            connection_status="connected",
            is_demo=False,
        )
    )
    db.add(
        RawMessage(
            id="raw_real_preserved",
            connected_account_id="acct_real_preserved",
            external_message_id="gmail:acct_real_preserved:same-id",
            platform="gmail",
            raw_payload_json="{}",
            received_at=now_iso(),
        )
    )
    db.add(
        UnifiedMessage(
            id="gmail_acct_real_preserved_same-id",
            raw_message_id="raw_real_preserved",
            connected_account_id="acct_real_preserved",
            platform="gmail",
            thread_key="gmail_thread_acct_real_preserved_thread",
            sender_name="Real Sender",
            sender_identifier="sender@example.test",
            subject="Preserve me",
            body_text="Real connector cache",
            sent_at=now_iso(),
            received_at=now_iso(),
        )
    )
    db.add(
        OAuthConnection(
            id="oauth_preserved",
            user_id="user_001",
            provider="google",
            account_email="real@example.test",
            scopes_json="[]",
            status="connected",
            connected_account_id="acct_real_preserved",
            updated_at=now_iso(),
        )
    )
    db.add(
        EncryptedToken(
            id="token_preserved",
            oauth_connection_id="oauth_preserved",
            provider="google",
            encrypted_access_token="ciphertext-only",
            scopes_json="[]",
        )
    )
    db.add(
        RealSyncRun(
            id="sync_preserved",
            oauth_connection_id="oauth_preserved",
            provider="google",
            sync_type="gmail_messages",
            status="completed",
        )
    )
    db.add(
        ProviderMessageCursor(
            id="cursor_preserved",
            oauth_connection_id="oauth_preserved",
            provider="google",
            resource_type="gmail_messages",
        )
    )
    db.add(
        RealSyncedItem(
            id="real_item_preserved",
            oauth_connection_id="oauth_preserved",
            provider="google",
            local_target_type="unified_message",
            local_target_id="gmail_acct_real_preserved_same-id",
            provider_resource_id="same-id",
        )
    )
    db.commit()


def test_force_demo_reseed_preserves_real_connector_state(db):
    _add_real_state(db)
    first = seed_database(db, force=True)
    second = seed_database(db, force=True)

    assert first["accounts"] == 6
    assert first["messages"] == 80
    assert second["accounts"] == 6
    assert second["messages"] == 80
    assert db.get(OAuthConnection, "oauth_preserved") is not None
    assert db.get(EncryptedToken, "token_preserved") is not None
    assert db.get(RealSyncRun, "sync_preserved") is not None
    assert db.get(ProviderMessageCursor, "cursor_preserved") is not None
    assert db.get(RealSyncedItem, "real_item_preserved") is not None
    assert db.get(ConnectedAccount, "acct_real_preserved") is not None
    assert db.get(UnifiedMessage, "gmail_acct_real_preserved_same-id") is not None


def test_force_demo_reseed_restores_six_accounts_and_eighty_messages(db):
    seed_database(db, force=True)
    demo_accounts = db.scalar(
        select(func.count())
        .select_from(ConnectedAccount)
        .where(ConnectedAccount.is_demo.is_(True))
    )
    demo_messages = db.scalar(
        select(func.count())
        .select_from(UnifiedMessage)
        .join(
            ConnectedAccount,
            ConnectedAccount.id == UnifiedMessage.connected_account_id,
        )
        .where(ConnectedAccount.is_demo.is_(True))
    )
    assert demo_accounts == 6
    assert demo_messages == 80
