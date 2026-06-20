from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ConnectedAccount, MessageEntity, NotificationEvent, RiskAssessment, RiskReason, UnifiedMessage


def assessment_dict(db: Session, assessment: RiskAssessment) -> dict:
    reasons = db.scalars(
        select(RiskReason).where(RiskReason.assessment_id == assessment.id).order_by(RiskReason.points.desc())
    ).all()
    return {
        "id": assessment.id,
        "message_id": assessment.message_id,
        "urgency_score": assessment.urgency_score,
        "risk_score": assessment.risk_score,
        "action_score": assessment.action_score,
        "priority_score": assessment.priority_score,
        "priority_level": assessment.priority_level,
        "recommended_action": assessment.recommended_action,
        "summary": assessment.summary,
        "reasons": [
            {
                "reason_code": item.reason_code,
                "reason_type": item.reason_type,
                "points": item.points,
                "explanation": item.explanation,
            }
            for item in reasons
        ],
    }


def message_dict(db: Session, message: UnifiedMessage, include_detail: bool = False) -> dict:
    account = db.get(ConnectedAccount, message.connected_account_id)
    assessment = db.scalar(select(RiskAssessment).where(RiskAssessment.message_id == message.id))
    result = {
        "id": message.id,
        "connected_account_id": message.connected_account_id,
        "account_label": account.account_label if account else "",
        "is_demo": account.is_demo if account else True,
        "platform": message.platform,
        "thread_key": message.thread_key,
        "sender_name": message.sender_name,
        "sender_identifier": message.sender_identifier,
        "subject": message.subject,
        "body_text": message.body_text,
        "received_at": message.received_at,
        "sent_at": message.sent_at,
        "is_read": message.is_read,
        "has_attachments": message.has_attachments,
        "assessment": assessment_dict(db, assessment) if assessment else None,
    }
    if include_detail:
        entities = db.scalars(select(MessageEntity).where(MessageEntity.message_id == message.id)).all()
        result["entities"] = [
            {
                "entity_type": entity.entity_type,
                "entity_value": entity.entity_value,
                "normalized_value": entity.normalized_value,
                "confidence": entity.confidence,
            }
            for entity in entities
        ]
    return result


def notification_dict(db: Session, notification: NotificationEvent) -> dict:
    message = db.get(UnifiedMessage, notification.message_id)
    account = db.get(ConnectedAccount, message.connected_account_id) if message else None
    assessment = db.get(RiskAssessment, notification.assessment_id)
    return {
        "id": notification.id,
        "message_id": notification.message_id,
        "notification_type": notification.notification_type,
        "priority_level": notification.priority_level,
        "title": notification.title,
        "body": notification.body,
        "status": notification.status,
        "scheduled_for": notification.scheduled_for,
        "snoozed_until": notification.snoozed_until,
        "created_at": notification.created_at,
        "sender_name": message.sender_name if message else "",
        "platform": message.platform if message else "",
        "account_label": account.account_label if account else "",
        "recommended_action": assessment.recommended_action if assessment else "",
        "reasons": assessment_dict(db, assessment)["reasons"][:3] if assessment else [],
    }


def parse_json(value: str | None, fallback=None):
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback

