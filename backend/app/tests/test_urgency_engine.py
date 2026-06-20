import pytest

from app.services.urgency_engine import score_urgency


@pytest.mark.parametrize(
    "text,minimum,code",
    [
        ("This is urgent, reply ASAP", 30, "urgent_language"),
        ("Please send this by EOD today", 35, "deadline_today"),
        ("The deadline is tomorrow", 25, "deadline_tomorrow"),
        ("Security alert from an unknown device", 40, "security_alert"),
        ("BANK ALERT: payment failed", 35, "financial_risk"),
    ],
)
def test_urgency_signals(text, minimum, code):
    score, reasons = score_urgency(text)
    assert score >= minimum
    assert code in {r["reason_code"] for r in reasons}


def test_neutral_message_has_no_urgency():
    assert score_urgency("Thanks for the update")[0] == 0

