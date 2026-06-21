from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import RawMessage, RiskAssessment, RiskReason


def run_evaluation(db: Session, write_report: bool = False) -> dict:
    raw_messages = db.scalars(select(RawMessage)).all()
    labeled_count = 0
    ignored_unlabeled_count = 0
    priority_hits = action_hits = reason_hits = reason_total = 0
    p0_true = p0_pred = p0_correct = 0
    schedule_total = schedule_hits = newsletter_total = newsletter_hits = 0
    details = []
    for raw in raw_messages:
        payload = json.loads(raw.raw_payload_json)
        expected = payload.get("expected")
        if not expected:
            ignored_unlabeled_count += 1
            continue
        labeled_count += 1
        assessment = db.scalar(select(RiskAssessment).where(RiskAssessment.message_id == payload["id"]))
        if not assessment:
            continue
        actual_codes = {
            item.reason_code
            for item in db.scalars(select(RiskReason).where(RiskReason.assessment_id == assessment.id)).all()
        }
        priority_ok = assessment.priority_level == expected["priority_level"]
        action_ok = assessment.recommended_action == expected["recommended_action"]
        priority_hits += int(priority_ok)
        action_hits += int(action_ok)
        expected_codes = set(expected.get("reason_codes", []))
        reason_hits += len(expected_codes & actual_codes)
        reason_total += len(expected_codes)
        if expected["priority_level"] == "P0_IMMEDIATE":
            p0_true += 1
        if assessment.priority_level == "P0_IMMEDIATE":
            p0_pred += 1
        if expected["priority_level"] == assessment.priority_level == "P0_IMMEDIATE":
            p0_correct += 1
        if payload["category"] in {"scheduling", "rescheduling", "calendar_conflict"}:
            schedule_total += 1
            schedule_hits += int(assessment.recommended_action == "send_to_scheduling_review")
        if payload["category"] == "newsletter":
            newsletter_total += 1
            newsletter_hits += int(assessment.priority_level in {"P2_DIGEST", "P3_LOW"})
        details.append({"message_id": payload["id"], "priority_ok": priority_ok, "routing_ok": action_ok})

    metrics = {
        "total_messages": labeled_count,
        "labeled_count": labeled_count,
        "ignored_unlabeled_count": ignored_unlabeled_count,
        "priority_accuracy": round(priority_hits / labeled_count, 3) if labeled_count else 0,
        "action_routing_accuracy": round(action_hits / labeled_count, 3) if labeled_count else 0,
        "p0_precision": round(p0_correct / p0_pred, 3) if p0_pred else 0,
        "p0_recall": round(p0_correct / p0_true, 3) if p0_true else 0,
        "reason_recall": round(reason_hits / reason_total, 3) if reason_total else None,
        "scheduling_routing_accuracy": round(schedule_hits / schedule_total, 3) if schedule_total else 0,
        "newsletter_suppression_accuracy": round(newsletter_hits / newsletter_total, 3) if newsletter_total else 0,
        "details": details,
    }
    return metrics
