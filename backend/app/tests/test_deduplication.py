from app.services.thread_deduper import is_duplicate


def test_duplicate_copy_detected():
    first = {"external_message_id": "one", "subject": "Security alert", "body_text": "New sign-in from unknown device"}
    second = {"external_message_id": "two", "subject": "Re: Security alert", "body_text": "New sign-in from unknown device"}
    assert is_duplicate(first, second)


def test_distinct_messages_not_deduplicated():
    assert not is_duplicate(
        {"external_message_id": "one", "subject": "Lunch", "body_text": "Tacos?"},
        {"external_message_id": "two", "subject": "Invoice", "body_text": "Payment failed"},
    )

