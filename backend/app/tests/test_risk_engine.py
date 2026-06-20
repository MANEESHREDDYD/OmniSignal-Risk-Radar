import pytest

from app.services.risk_engine import score_risk


@pytest.mark.parametrize(
    "text,category,code",
    [
        ("Security alert: unknown device", "", "security_alert"),
        ("Your card transaction may be fraud", "", "financial_risk"),
        ("International student immigration compliance", "", "legal_or_compliance"),
        ("Can we meet in person? Which time zone?", "scheduling", "timezone_unclear"),
    ],
)
def test_risk_signals(text, category, code):
    _, reasons = score_risk(text, category=category)
    assert code in {r["reason_code"] for r in reasons}


def test_newsletter_does_not_create_risk():
    assert score_risk("Weekly newsletter. Unsubscribe here.")[0] == 0

