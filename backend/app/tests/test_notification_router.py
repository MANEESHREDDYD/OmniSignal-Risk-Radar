from app.services.notification_router import route_notification


def assessment(level, codes=()):
    return {"priority_level": level, "reasons": [{"reason_code": code} for code in codes]}


def test_p0_notifies_now():
    assert route_notification(assessment("P0_IMMEDIATE")) == "notify_now"


def test_p1_scheduling_routes_to_review():
    assert route_notification(assessment("P1_TODAY", ["timezone_unclear"])) == "send_to_scheduling_review"


def test_p2_goes_to_digest():
    assert route_notification(assessment("P2_DIGEST")) == "add_to_digest"


def test_p3_is_quiet():
    assert route_notification(assessment("P3_LOW")) == "ignore_low_priority"

