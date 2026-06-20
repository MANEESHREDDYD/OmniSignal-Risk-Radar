from __future__ import annotations

from typing import Any


def route_notification(assessment: dict[str, Any]) -> str:
    level = assessment["priority_level"]
    codes = {r["reason_code"] for r in assessment.get("reasons", [])}
    if level == "P0_IMMEDIATE":
        return "notify_now"
    if level == "P1_TODAY":
        if codes & {"reschedule_request", "calendar_conflict", "timezone_unclear", "location_ambiguous"}:
            return "send_to_scheduling_review"
        return "review_today"
    if level == "P2_DIGEST":
        return "add_to_digest"
    return "ignore_low_priority"


def notification_copy(message: dict[str, Any], assessment: dict[str, Any]) -> tuple[str, str]:
    reasons = assessment.get("reasons", [])
    short_reason = reasons[0]["explanation"].rstrip(".") if reasons else "priority signal detected"
    sender = message.get("sender_name") or "A sender"
    action = assessment["recommended_action"].replace("_", " ")
    if assessment["priority_level"] == "P0_IMMEDIATE":
        return (
            f"Immediate action needed: {short_reason[:52]}",
            f'{sender} sent a message that may require immediate attention: "{assessment["summary"]}"',
        )
    if assessment["priority_level"] == "P1_TODAY":
        if action == "send to scheduling review":
            return ("Scheduling review needed", f"This request has scheduling risk factors. Open triage to resolve the ambiguity.")
        return (f"Needs attention today: {short_reason[:52]}", f"{sender} may be waiting on you. Recommended action: {action}.")
    return ("Added to digest", "This message does not appear urgent but may be useful later.")
