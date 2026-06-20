from __future__ import annotations

from typing import Any

from .action_detector import score_action
from .risk_engine import score_risk
from .urgency_engine import score_urgency

NEWSLETTER_WORDS = ["newsletter", "unsubscribe", "weekly digest", "promotion", "special offer"]
SCHEDULING_CODES = {"scheduling_request", "reschedule_request", "calendar_conflict", "timezone_unclear", "location_ambiguous"}


def _merge_reasons(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for group in groups:
        for reason in group:
            current = merged.get(reason["reason_code"])
            if current is None or reason["points"] > current["points"]:
                merged[reason["reason_code"]] = reason
    return list(merged.values())


def assess_message(message: dict[str, Any]) -> dict[str, Any]:
    text = f"{message.get('subject') or ''} {message.get('body_text') or ''}".strip()
    category = message.get("category", "")
    sender = f"{message.get('sender_name') or ''} {message.get('sender_identifier') or ''}"
    important = category in {"recruiter", "customer_vip"} or any(k in sender.lower() for k in ["recruit", "founder", "investor", "customer"])
    urgency, urgency_reasons = score_urgency(text, category)
    risk, risk_reasons = score_risk(text, sender, category)
    action, action_reasons = score_action(text, important)
    reasons = _merge_reasons(urgency_reasons, risk_reasons, action_reasons)
    lowered = text.lower()
    newsletter = category == "newsletter" or any(word in lowered for word in NEWSLETTER_WORDS)
    if newsletter:
        reasons.append(
            {
                "reason_code": "newsletter",
                "reason_type": "platform_signal",
                "points": -20,
                "explanation": "Bulk newsletter language lowers interruption priority.",
            }
        )
        if action == 0:
            reasons.append(
                {
                    "reason_code": "no_action_required",
                    "reason_type": "action_needed",
                    "points": 0,
                    "explanation": "No direct request for the user was detected.",
                }
            )

    priority_score = min(100, round(urgency * 0.40 + risk * 0.35 + action * 0.25))
    codes = {r["reason_code"] for r in reasons}
    if priority_score >= 80:
        level = "P0_IMMEDIATE"
    elif priority_score >= 60:
        level = "P1_TODAY"
    elif priority_score >= 35:
        level = "P2_DIGEST"
    else:
        level = "P3_LOW"

    # Safety-oriented deterministic overrides.
    if "security_alert" in codes or ("financial_risk" in codes and "large_amount" in codes):
        level = "P0_IMMEDIATE"
        priority_score = max(priority_score, 82)
    if "deadline_today" in codes and action >= 20:
        level = "P0_IMMEDIATE"
        priority_score = max(priority_score, 80)
    if {"deadline_tomorrow", "legal_or_compliance", "document_request"}.issubset(codes):
        level = "P0_IMMEDIATE"
        priority_score = max(priority_score, 80)
    if codes & SCHEDULING_CODES and ({"timezone_unclear", "location_ambiguous", "calendar_conflict"} & codes):
        if level not in {"P0_IMMEDIATE"}:
            level = "P1_TODAY"
            priority_score = max(priority_score, 62)
    if codes & {"recruiter_sender", "repeated_follow_up"} and level not in {"P0_IMMEDIATE"}:
        level = "P1_TODAY"
        priority_score = max(priority_score, 60)
    if newsletter and not (codes & {"security_alert", "financial_risk", "deadline_today"}):
        level = "P3_LOW" if action == 0 else "P2_DIGEST"
        priority_score = min(priority_score, 34 if action == 0 else 59)

    if level == "P0_IMMEDIATE":
        recommended = "notify_now"
    elif level == "P1_TODAY":
        scheduling_review = category in {"scheduling", "rescheduling", "calendar_conflict"} or bool(
            codes & {"reschedule_request", "calendar_conflict", "timezone_unclear", "location_ambiguous"}
        )
        recommended = "send_to_scheduling_review" if scheduling_review else "review_today"
    elif level == "P2_DIGEST":
        recommended = "add_to_digest"
    else:
        recommended = "ignore_low_priority"

    summary_source = message.get("body_text") or message.get("subject") or ""
    summary = summary_source[:180] + ("…" if len(summary_source) > 180 else "")
    return {
        "urgency_score": urgency,
        "risk_score": risk,
        "action_score": action,
        "priority_score": priority_score,
        "priority_level": level,
        "recommended_action": recommended,
        "summary": summary,
        "reasons": sorted(reasons, key=lambda r: r["points"], reverse=True),
    }
