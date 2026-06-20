from __future__ import annotations

import json
import uuid
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import (
    AuditLog,
    ConnectedAccount,
    MessageEntity,
    MessageThread,
    NotificationEvent,
    RawMessage,
    RiskAssessment,
    RiskReason,
    UnifiedMessage,
    UserActionItem,
    UserRule,
    now_iso,
)
from .seed_data import DEFAULT_RULES, DEMO_ACCOUNTS, get_demo_messages
from .services.audit_logger import log_action
from .services.entity_extractor import extract_entities
from .services.message_normalizer import canonical_subject, normalize_message
from .services.notification_router import notification_copy, route_notification
from .services.priority_engine import assess_message


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def seed_database(db: Session, force: bool = False) -> dict:
    Base.metadata.create_all(bind=engine)
    existing = db.scalar(select(func.count()).select_from(UnifiedMessage)) or 0
    if existing and not force:
        return {"accounts": db.scalar(select(func.count()).select_from(ConnectedAccount)), "messages": existing, "seeded": False}
    if force:
        for model in [AuditLog, NotificationEvent, RiskReason, RiskAssessment, MessageEntity, UserActionItem, MessageThread, UnifiedMessage, RawMessage, UserRule, ConnectedAccount]:
            db.query(model).delete()
        db.commit()

    for account in DEMO_ACCOUNTS:
        db.add(ConnectedAccount(**account, last_sync_at=now_iso()))
    for rule_id, name, rule_type, conditions, action in DEFAULT_RULES:
        db.add(UserRule(id=rule_id, rule_name=name, rule_type=rule_type, conditions_json=json.dumps(conditions), action_json=json.dumps(action)))
    db.flush()

    thread_groups: dict[str, list[dict]] = defaultdict(list)
    for raw in get_demo_messages():
        db.add(
            RawMessage(
                id=f"raw_{raw['id']}",
                connected_account_id=raw["connected_account_id"],
                external_message_id=raw["external_message_id"],
                platform=raw["platform"],
                raw_payload_json=json.dumps(raw),
                received_at=raw["received_at"],
            )
        )
        normalized = normalize_message(raw)
        message = UnifiedMessage(
            id=raw["id"],
            raw_message_id=normalized["raw_message_id"],
            connected_account_id=normalized["connected_account_id"],
            platform=normalized["platform"],
            thread_key=normalized["thread_key"],
            sender_name=normalized["sender_name"],
            sender_identifier=normalized["sender_identifier"],
            recipient_identifiers_json=json.dumps(normalized["recipient_identifiers"]),
            subject=normalized["subject"],
            body_text=normalized["body_text"],
            message_url=normalized["message_url"],
            sent_at=normalized["sent_at"],
            received_at=normalized["received_at"],
            has_attachments=normalized["has_attachments"],
            is_read=normalized["is_read"],
        )
        db.add(message)
        db.flush()
        analysis_input = {**normalized, "category": raw["category"]}
        assessment_data = assess_message(analysis_input)
        assessment_id = f"assess_{raw['id']}"
        db.add(RiskAssessment(id=assessment_id, message_id=raw["id"], **{k: v for k, v in assessment_data.items() if k != "reasons"}))
        for reason in assessment_data["reasons"]:
            db.add(RiskReason(id=_uid("reason"), assessment_id=assessment_id, **reason))
        for entity in extract_entities(normalized):
            db.add(MessageEntity(id=_uid("entity"), message_id=raw["id"], **entity))

        route = route_notification(assessment_data)
        if route != "ignore_low_priority":
            title, body = notification_copy(normalized, assessment_data)
            db.add(
                NotificationEvent(
                    id=f"notif_{raw['id']}",
                    message_id=raw["id"],
                    assessment_id=assessment_id,
                    notification_type=route,
                    priority_level=assessment_data["priority_level"],
                    title=title,
                    body=body,
                    status="delivered",
                    delivered_at=now_iso(),
                )
            )
        if assessment_data["action_score"] >= 30:
            db.add(
                UserActionItem(
                    id=f"task_{raw['id']}",
                    message_id=raw["id"],
                    title=f"Follow up: {normalized['subject'] or normalized['sender_name']}",
                    description=assessment_data["summary"],
                    source_platform=normalized["platform"],
                )
            )
        log_action(db, "Risk Engine", "Scored message", "message", raw["id"], after={"priority": assessment_data["priority_level"], "score": assessment_data["priority_score"]})
        thread_groups[normalized["thread_key"]].append(normalized)

    for key, group in thread_groups.items():
        platforms = sorted({item["platform"] for item in group})
        participants = sorted({item["sender_identifier"] for item in group})
        db.add(
            MessageThread(
                id=f"thread_{key}",
                canonical_subject=canonical_subject(group[0]["subject"], group[0]["body_text"]),
                thread_key=key,
                platform_mix_json=json.dumps(platforms),
                participant_identifiers_json=json.dumps(participants),
                first_message_at=min(item["sent_at"] for item in group),
                last_message_at=max(item["sent_at"] for item in group),
                message_count=len(group),
            )
        )
    db.commit()
    return {"accounts": len(DEMO_ACCOUNTS), "messages": 80, "seeded": True}


if __name__ == "__main__":
    with SessionLocal() as session:
        print(seed_database(session, force=True))
