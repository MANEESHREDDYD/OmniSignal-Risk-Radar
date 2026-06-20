import pytest

from app.services.priority_engine import assess_message


@pytest.mark.parametrize(
    "message,expected",
    [
        ({"subject": "Security alert", "body_text": "Unknown device. Secure your account immediately."}, "P0_IMMEDIATE"),
        ({"subject": "Due today", "body_text": "Please confirm by EOD today."}, "P0_IMMEDIATE"),
        ({"subject": "Recruiter", "body_text": "Interview tomorrow. Please confirm.", "sender_name": "Acme Recruiter", "category": "recruiter"}, "P1_TODAY"),
        ({"subject": "Weekly newsletter", "body_text": "Stories and promotions. Unsubscribe.", "category": "newsletter"}, "P3_LOW"),
        ({"subject": "Meet?", "body_text": "Can we meet Tuesday? Which time zone? In person maybe.", "category": "scheduling"}, "P1_TODAY"),
    ],
)
def test_priority_overrides(message, expected):
    assert assess_message(message)["priority_level"] == expected

