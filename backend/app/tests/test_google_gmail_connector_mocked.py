import base64

from app.services.connectors.google_gmail_connector import (
    GoogleGmailConnector,
    normalize_gmail_message,
)


def _b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode()


class FakeGmailClient:
    """Read-only mock. Records calls; exposes NO send/modify methods."""

    def __init__(self, listing, messages):
        self._listing = listing
        self._messages = messages
        self.calls = []

    def list_messages(self, max_results):
        self.calls.append(("list_messages", max_results))
        return self._listing

    def get_message(self, message_id):
        self.calls.append(("get_message", message_id))
        return self._messages.get(message_id)


SAMPLE = {
    "id": "m1",
    "threadId": "t1",
    "labelIds": ["INBOX", "UNREAD"],
    "snippet": "snippet text",
    "internalDate": "1700000000000",
    "payload": {
        "mimeType": "text/plain",
        "headers": [
            {"name": "From", "value": "Alice Smith <alice@example.com>"},
            {"name": "To", "value": "me@example.com, team@example.com"},
            {"name": "Subject", "value": "Quarterly report due"},
        ],
        "body": {"data": _b64("Please review the report by Friday.")},
    },
}


def test_converts_mocked_message_to_normalized():
    client = FakeGmailClient({"messages": [{"id": "m1"}]}, {"m1": SAMPLE})
    connector = GoogleGmailConnector(client)
    items = connector.fetch_normalized("acct_1")
    assert len(items) == 1
    item = items[0]
    assert item["platform"] == "gmail"
    assert item["sender_name"] == "Alice Smith"
    assert item["sender_identifier"] == "alice@example.com"
    assert "me@example.com" in item["recipient_identifiers"]
    assert item["subject"] == "Quarterly report due"
    assert "review the report" in item["body_text"]
    assert item["provider_resource_id"] == "m1"
    assert item["external_message_id"] == "gmail:acct_1:m1"
    assert item["is_read"] is False  # UNREAD label present


def test_connector_only_uses_read_methods():
    client = FakeGmailClient({"messages": [{"id": "m1"}]}, {"m1": SAMPLE})
    GoogleGmailConnector(client).fetch_normalized("acct_1")
    # No send/modify/delete were ever called.
    assert all(name in {"list_messages", "get_message"} for name, _ in client.calls)
    assert not hasattr(client, "send_message")
    assert not hasattr(client, "modify_message")


def test_handles_empty_inbox():
    client = FakeGmailClient({}, {})
    assert GoogleGmailConnector(client).fetch_normalized("acct_1") == []


def test_handles_malformed_message_safely():
    # One id resolves to None (e.g. fetch failed) — must be skipped, not crash.
    client = FakeGmailClient({"messages": [{"id": "m1"}, {"id": "bad"}]}, {"m1": SAMPLE, "bad": None})
    items = GoogleGmailConnector(client).fetch_normalized("acct_1")
    assert len(items) == 1


def test_body_is_truncated():
    big = dict(SAMPLE)
    big = {**SAMPLE, "id": "m2", "payload": {**SAMPLE["payload"], "body": {"data": _b64("x" * 10000)}}}
    item = normalize_gmail_message(big, "acct_1")
    assert len(item["body_text"]) <= 4000


def test_same_provider_id_is_scoped_per_google_account():
    first = normalize_gmail_message(SAMPLE, "acct_google_a")
    second = normalize_gmail_message(SAMPLE, "acct_google_b")
    assert first["id"] != second["id"]
    assert first["external_message_id"] != second["external_message_id"]
    assert first["thread_key"] != second["thread_key"]
