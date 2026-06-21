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
    SyncRun,
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
from .services.user_rule_engine import load_enabled_rules


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _delete_demo_data(db: Session) -> dict[str, int]:
    """Delete only synthetic demo rows while preserving all real connector state."""
    configured_demo_ids = {account["id"] for account in DEMO_ACCOUNTS}
    demo_accounts = db.scalars(
        select(ConnectedAccount).where(
            (ConnectedAccount.is_demo.is_(True))
            | (ConnectedAccount.id.in_(configured_demo_ids))
        )
    ).all()
    demo_account_ids = {account.id for account in demo_accounts}
    if not demo_account_ids:
        return {"accounts_deleted": 0, "messages_deleted": 0}

    demo_messages = db.scalars(
        select(UnifiedMessage).where(
            UnifiedMessage.connected_account_id.in_(demo_account_ids)
        )
    ).all()
    message_ids = {message.id for message in demo_messages}
    raw_ids = {
        raw.id
        for raw in db.scalars(
            select(RawMessage).where(
                RawMessage.connected_account_id.in_(demo_account_ids)
            )
        ).all()
    }
    thread_keys = {message.thread_key for message in demo_messages if message.thread_key}

    assessments = (
        db.scalars(
            select(RiskAssessment).where(RiskAssessment.message_id.in_(message_ids))
        ).all()
        if message_ids
        else []
    )
    assessment_ids = {assessment.id for assessment in assessments}

    if assessment_ids:
        db.query(RiskReason).filter(
            RiskReason.assessment_id.in_(assessment_ids)
        ).delete(synchronize_session=False)
        db.query(NotificationEvent).filter(
            NotificationEvent.assessment_id.in_(assessment_ids)
        ).delete(synchronize_session=False)
    if message_ids:
        db.query(MessageEntity).filter(
            MessageEntity.message_id.in_(message_ids)
        ).delete(synchronize_session=False)
        db.query(UserActionItem).filter(
            UserActionItem.message_id.in_(message_ids)
        ).delete(synchronize_session=False)
        db.query(RiskAssessment).filter(
            RiskAssessment.message_id.in_(message_ids)
        ).delete(synchronize_session=False)
        db.query(UnifiedMessage).filter(
            UnifiedMessage.id.in_(message_ids)
        ).delete(synchronize_session=False)
    if raw_ids:
        db.query(RawMessage).filter(RawMessage.id.in_(raw_ids)).delete(
            synchronize_session=False
        )

    db.query(SyncRun).filter(
        SyncRun.connected_account_id.in_(demo_account_ids)
    ).delete(synchronize_session=False)
    default_rule_ids = {rule[0] for rule in DEFAULT_RULES}
    db.query(UserRule).filter(UserRule.id.in_(default_rule_ids)).delete(
        synchronize_session=False
    )
    db.query(ConnectedAccount).filter(
        ConnectedAccount.id.in_(demo_account_ids)
    ).delete(synchronize_session=False)
    db.flush()

    # Delete only threads that no longer have any messages after demo cleanup.
    for thread_key in thread_keys:
        remaining = db.scalar(
            select(func.count())
            .select_from(UnifiedMessage)
            .where(UnifiedMessage.thread_key == thread_key)
        ) or 0
        if remaining == 0:
            db.query(MessageThread).filter(
                MessageThread.thread_key == thread_key
            ).delete(synchronize_session=False)

    return {
        "accounts_deleted": len(demo_account_ids),
        "messages_deleted": len(message_ids),
    }


def seed_database(db: Session, force: bool = False) -> dict:
    Base.metadata.create_all(bind=engine)
    demo_account_ids = {account["id"] for account in DEMO_ACCOUNTS}
    demo_accounts = db.scalar(
        select(func.count())
        .select_from(ConnectedAccount)
        .where(ConnectedAccount.id.in_(demo_account_ids))
    ) or 0
    demo_messages = db.scalar(
        select(func.count())
        .select_from(UnifiedMessage)
        .where(UnifiedMessage.connected_account_id.in_(demo_account_ids))
    ) or 0
    if demo_accounts == len(DEMO_ACCOUNTS) and demo_messages == 80 and not force:
        return {"accounts": demo_accounts, "messages": demo_messages, "seeded": False}
    if force or demo_accounts or demo_messages:
        _delete_demo_data(db)
        db.commit()

    default_rule_ids = {rule[0] for rule in DEFAULT_RULES}
    db.query(UserRule).filter(UserRule.id.in_(default_rule_ids)).delete(
        synchronize_session=False
    )
    for account in DEMO_ACCOUNTS:
        db.add(ConnectedAccount(**account, last_sync_at=now_iso()))
    for rule_id, name, rule_type, conditions, action in DEFAULT_RULES:
        db.add(UserRule(id=rule_id, rule_name=name, rule_type=rule_type, conditions_json=json.dumps(conditions), action_json=json.dumps(action)))
    db.flush()
    user_rules = load_enabled_rules(db)

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
        assessment_data = assess_message(analysis_input, user_rules=user_rules)
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
