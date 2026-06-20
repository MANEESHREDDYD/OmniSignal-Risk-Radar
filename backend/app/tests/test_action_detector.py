import pytest

from app.services.action_detector import score_action


@pytest.mark.parametrize(
    "text,code",
    [
        ("Please confirm your availability", "confirmation_required"),
        ("Please submit documents", "document_request"),
        ("Can we schedule a meeting?", "scheduling_request"),
        ("Can we reschedule?", "reschedule_request"),
    ],
)
def test_action_phrases(text, code):
    score, reasons = score_action(text)
    assert score >= 25
    assert code in {r["reason_code"] for r in reasons}


def test_no_action():
    assert score_action("FYI, the report is attached.")[0] == 0

