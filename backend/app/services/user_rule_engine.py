"""Deterministic user-rule matching for message assessment.

Rules are intentionally small and explainable. They can match sender text,
subject/body keywords, or an already-detected reason. Actions may set a minimum
priority, cap an interruption at digest, mark a sender as VIP, or choose the
simulated scheduling-review marker.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import UserRule


PRIORITY_RANK = {
    "P3_LOW": 0,
    "P2_DIGEST": 1,
    "P1_TODAY": 2,
    "P0_IMMEDIATE": 3,
}
PRIORITY_MINIMUM_SCORE = {
    "P3_LOW": 0,
    "P2_DIGEST": 35,
    "P1_TODAY": 60,
    "P0_IMMEDIATE": 80,
}


def load_enabled_rules(db: Session, user_id: str = "user_001") -> list[dict[str, Any]]:
    rows = db.scalars(
        select(UserRule).where(
            UserRule.user_id == user_id,
            UserRule.is_enabled.is_(True),
        )
    ).all()
    return [
        {
            "id": row.id,
            "name": row.rule_name,
            "conditions": json.loads(row.conditions_json or "{}"),
            "action": json.loads(row.action_json or "{}"),
        }
        for row in rows
    ]


def _sender_type_matches(sender: str, sender_type: str) -> bool:
    groups = {
        "recruiter": ("recruit", "talent", "hiring"),
        "official": ("international student", "registrar", "compliance", "legal"),
        "vip": ("founder", "investor", "customer", "executive"),
    }
    return any(token in sender for token in groups.get(sender_type.lower(), (sender_type.lower(),)))


def rule_matches(
    message: dict[str, Any],
    conditions: dict[str, Any],
    reason_codes: set[str],
) -> bool:
    sender_name = (message.get("sender_name") or "").lower().strip()
    sender_identifier = (message.get("sender_identifier") or "").lower().strip()
    sender = f"{sender_name} {sender_identifier}".strip()
    subject = (message.get("subject") or "").lower()
    body = (message.get("body_text") or "").lower()
    combined = f"{subject} {body}"

    checks: list[bool] = []
    if value := conditions.get("sender_contains"):
        checks.append(str(value).lower() in sender)
    if value := conditions.get("sender_equals"):
        expected = str(value).lower().strip()
        checks.append(expected in {sender_name, sender_identifier, sender})
    if value := conditions.get("keyword_contains"):
        checks.append(str(value).lower() in combined)
    if value := conditions.get("subject_contains"):
        checks.append(str(value).lower() in subject)
    if value := conditions.get("body_contains"):
        checks.append(str(value).lower() in body)
    if value := conditions.get("reason"):
        checks.append(str(value) in reason_codes)
    if value := conditions.get("sender_type"):
        checks.append(_sender_type_matches(sender, str(value)))
    return bool(checks) and all(checks)


def apply_user_rules(
    message: dict[str, Any],
    assessment: dict[str, Any],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    reason_codes = {reason["reason_code"] for reason in assessment["reasons"]}
    for rule in rules:
        conditions = rule.get("conditions") or {}
        action = rule.get("action") or {}
        if not rule_matches(message, conditions, reason_codes):
            continue

        rule_id = str(rule.get("id") or "custom")
        normalized_rule_id = rule_id[5:] if rule_id.startswith("rule_") else rule_id
        rule_name = str(rule.get("name") or "User rule")
        reason = {
            "reason_code": f"user_rule_{normalized_rule_id}",
            "reason_type": "user_rule",
            "points": 0,
            "explanation": f'Enabled user rule matched: "{rule_name}".',
        }
        if reason["reason_code"] not in reason_codes:
            assessment["reasons"].append(reason)
            reason_codes.add(reason["reason_code"])

        if action.get("mark_vip"):
            if "vip_sender" not in reason_codes:
                assessment["reasons"].append(
                    {
                        "reason_code": "vip_sender",
                        "reason_type": "sender_importance",
                        "points": 20,
                        "explanation": "An enabled user rule marks this sender as VIP.",
                    }
                )
                reason_codes.add("vip_sender")
            _raise_minimum(assessment, "P1_TODAY")

        minimum = action.get("minimum_priority") or action.get("force_priority_minimum")
        if minimum in PRIORITY_RANK:
            _raise_minimum(assessment, minimum)

        if action.get("suppress_to_digest"):
            # Safety signals cannot be suppressed by a user rule.
            if not reason_codes & {"security_alert", "financial_risk"}:
                assessment["priority_level"] = "P2_DIGEST"
                assessment["priority_score"] = min(
                    59, max(35, assessment["priority_score"])
                )
                assessment["recommended_action"] = "add_to_digest"

        if action.get("route") in {"scheduling_review", "send_to_scheduling_review"}:
            assessment["recommended_action"] = "send_to_scheduling_review"

    assessment["reasons"] = sorted(
        assessment["reasons"], key=lambda item: item["points"], reverse=True
    )
    return assessment


def _raise_minimum(assessment: dict[str, Any], minimum: str) -> None:
    if PRIORITY_RANK[assessment["priority_level"]] < PRIORITY_RANK[minimum]:
        assessment["priority_level"] = minimum
        assessment["priority_score"] = max(
            assessment["priority_score"], PRIORITY_MINIMUM_SCORE[minimum]
        )
        assessment["recommended_action"] = {
            "P0_IMMEDIATE": "notify_now",
            "P1_TODAY": "review_today",
            "P2_DIGEST": "add_to_digest",
            "P3_LOW": "ignore_low_priority",
        }[minimum]
