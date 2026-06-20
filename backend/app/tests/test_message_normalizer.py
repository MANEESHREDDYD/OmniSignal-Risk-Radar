import pytest

from app.services.message_normalizer import normalize_message


@pytest.mark.parametrize(
    "platform,body_key",
    [("gmail", "body_text"), ("outlook", "body"), ("sms", "text"), ("imessage", "text"), ("calendar", "description")],
)
def test_platform_payload_normalizes(platform, body_key):
    payload = {
        "id": f"{platform}_1",
        "connected_account_id": "acct_1",
        "platform": platform,
        "sender_name": "Demo Sender",
        "sender_identifier": "sender@example.com",
        body_key: "Please confirm tomorrow at 2 PM.",
        "sent_at": "2026-06-20T10:00:00-04:00",
    }
    result = normalize_message(payload)
    assert result["platform"] == platform
    assert result["body_text"] == "Please confirm tomorrow at 2 PM."
    assert result["thread_key"]

