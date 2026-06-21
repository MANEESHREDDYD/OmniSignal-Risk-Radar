"""Ingest real (read-only) synced items through the existing scoring pipeline.

Reuses the same normalization, risk scoring, notification routing, entity
extraction, and audit flow as the synthetic demo, so real messages appear in the
unified inbox / radar / notifications exactly like demo data — but tagged as real
and traceable for per-connection cache deletion.
"""

from __future__ import annotations

import json
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    MessageEntity,
    MessageThread,
    NotificationEvent,
    OAuthConnection,
    RawMessage,
    RealSyncedItem,
    RiskAssessment,
    RiskReason,
    UnifiedMessage,
    UserActionItem,
    now_iso,
)
from .audit_logger import log_action
from .entity_extractor import extract_entities
from .message_normalizer import canonical_subject, normalize_message
from .notification_router import notification_copy, route_notification
from .priority_engine import assess_message
from .user_rule_engine import load_enabled_rules


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _upsert_thread(db: Session, normalized: dict) -> None:
    key = normalized["thread_key"]
    thread = db.scalar(select(MessageThread).where(MessageThread.thread_key == key))
    if thread:
        thread.last_message_at = max(thread.last_message_at, normalized["sent_at"] or thread.last_message_at)
        thread.message_count += 1
        return
    db.add(
        MessageThread(
            id=f"thread_{key}",
            canonical_subject=canonical_subject(normalized["subject"], normalized["body_text"]),
            thread_key=key,
            platform_mix_json=json.dumps([normalized["platform"]]),
            participant_identifiers_json=json.dumps([normalized["sender_identifier"]]),
            first_message_at=normalized["sent_at"] or now_iso(),
            last_message_at=normalized["sent_at"] or now_iso(),
            message_count=1,
        )
    )


def ingest_real_items(
    db: Session,
    *,
    connection: OAuthConnection,
    connected_account_id: str,
    items: list[dict],
) -> dict[str, int]:
    """Ingest normalized-raw payloads for one connection. Idempotent per message.

    Returns counts: ``seen`` and ``created``.
    """
    seen = 0
    created = 0
    user_rules = load_enabled_rules(db, connection.user_id)
    for raw in items:
        seen += 1
        external_id = raw["external_message_id"]
        existing = db.scalar(
            select(RawMessage).where(RawMessage.external_message_id == external_id)
        )
        if existing:
            continue  # already ingested — keep sync idempotent

        normalized = normalize_message(raw)
        raw_message_id = normalized["raw_message_id"]
        db.add(
            RawMessage(
                id=raw_message_id,
                connected_account_id=connected_account_id,
                external_message_id=external_id,
                platform=normalized["platform"],
                raw_payload_json=json.dumps(_redacted_payload(raw)),
                received_at=normalized["received_at"] or now_iso(),
            )
        )
        message = UnifiedMessage(
            id=normalized["id"],
            raw_message_id=raw_message_id,
            connected_account_id=connected_account_id,
            platform=normalized["platform"],
            thread_key=normalized["thread_key"],
            sender_name=normalized["sender_name"],
            sender_identifier=normalized["sender_identifier"],
            recipient_identifiers_json=json.dumps(normalized["recipient_identifiers"]),
            subject=normalized["subject"],
            body_text=normalized["body_text"],
            message_url=normalized["message_url"],
            sent_at=normalized["sent_at"] or now_iso(),
            received_at=normalized["received_at"] or now_iso(),
            has_attachments=normalized["has_attachments"],
            is_read=normalized["is_read"],
        )
        db.add(message)
        db.flush()

        analysis_input = {**normalized, "category": raw.get("category", "")}
        assessment_data = assess_message(analysis_input, user_rules=user_rules)
        assessment_id = _uid("assess")
        db.add(
            RiskAssessment(
                id=assessment_id,
                message_id=message.id,
                **{k: v for k, v in assessment_data.items() if k != "reasons"},
            )
        )
        for reason in assessment_data["reasons"]:
            db.add(RiskReason(id=_uid("reason"), assessment_id=assessment_id, **reason))
        for entity in extract_entities(normalized):
            db.add(MessageEntity(id=_uid("entity"), message_id=message.id, **entity))

        route = route_notification(assessment_data)
        if route != "ignore_low_priority":
            title, body = notification_copy(normalized, assessment_data)
            db.add(
                NotificationEvent(
                    id=_uid("notif"),
                    message_id=message.id,
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
                    id=_uid("task"),
                    message_id=message.id,
                    title=f"Follow up: {normalized['subject'] or normalized['sender_name']}",
                    description=assessment_data["summary"],
                    source_platform=normalized["platform"],
                )
            )

        # Traceability rows so we can delete this connection's real data only.
        db.add(
            RealSyncedItem(
                id=_uid("rsi"),
                oauth_connection_id=connection.id,
                provider=connection.provider,
                local_target_type="unified_message",
                local_target_id=message.id,
                provider_resource_id=raw.get("provider_resource_id"),
            )
        )
        _upsert_thread(db, normalized)
        log_action(
            db,
            "Real Connector",
            "Ingested real message",
            "message",
            message.id,
            after={"platform": normalized["platform"], "priority": assessment_data["priority_level"]},
        )
        created += 1
    return {"seen": seen, "created": created}


def delete_real_cache(db: Session, connection: OAuthConnection) -> dict[str, int]:
    """Delete locally synced real records for one connection only.

    Synthetic demo data (is_demo accounts and their messages) is never touched —
    we only remove unified messages tracked in ``real_synced_items`` for this
    connection, plus their dependent assessment/notification/entity rows.
    """
    items = db.scalars(
        select(RealSyncedItem).where(RealSyncedItem.oauth_connection_id == connection.id)
    ).all()
    message_ids = [i.local_target_id for i in items if i.local_target_type == "unified_message"]
    selected_thread_keys = {
        message.thread_key
        for message_id in message_ids
        if (message := db.get(UnifiedMessage, message_id)) is not None
        and message.connected_account_id == connection.connected_account_id
        and message.thread_key
    }
    deleted_messages = 0
    for message_id in message_ids:
        message = db.get(UnifiedMessage, message_id)
        if not message or message.connected_account_id != connection.connected_account_id:
            continue
        assessments = db.scalars(
            select(RiskAssessment).where(RiskAssessment.message_id == message_id)
        ).all()
        for assessment in assessments:
            for reason in db.scalars(
                select(RiskReason).where(RiskReason.assessment_id == assessment.id)
            ).all():
                db.delete(reason)
            db.delete(assessment)
        for entity in db.scalars(
            select(MessageEntity).where(MessageEntity.message_id == message_id)
        ).all():
            db.delete(entity)
        for notif in db.scalars(
            select(NotificationEvent).where(NotificationEvent.message_id == message_id)
        ).all():
            db.delete(notif)
        for task in db.scalars(
            select(UserActionItem).where(UserActionItem.message_id == message_id)
        ).all():
            db.delete(task)
        raw = db.get(RawMessage, message.raw_message_id)
        if raw:
            db.delete(raw)
        db.delete(message)
        deleted_messages += 1

    for item in items:
        db.delete(item)

    # Only consider threads referenced by the selected connection. Delete a
    # thread row only when no message from any account still references it.
    db.flush()
    threads_deleted = 0
    for thread_key in selected_thread_keys:
        remaining = db.scalar(
            select(UnifiedMessage.id).where(
                UnifiedMessage.thread_key == thread_key
            ).limit(1)
        )
        if remaining is None:
            thread = db.scalar(
                select(MessageThread).where(
                    MessageThread.thread_key == thread_key
                )
            )
            if thread:
                db.delete(thread)
                threads_deleted += 1

    return {
        "items_deleted": len(items),
        "messages_deleted": deleted_messages,
        "threads_deleted": threads_deleted,
    }


def _redacted_payload(raw: dict) -> dict:
    """Strip nothing secret here, but keep the stored payload compact & bounded.

    Tokens never reach this layer; we keep provider id and metadata, and the body
    is already truncated by the connector.
    """
    keep = {
        "external_message_id",
        "platform",
        "category",
        "subject",
        "sender_identifier",
        "sender_name",
        "recipient_identifiers",
        "sent_at",
        "received_at",
        "provider_resource_id",
        "labels",
        "event_start",
        "event_end",
        "event_location",
        "event_status",
    }
    return {k: v for k, v in raw.items() if k in keep}
