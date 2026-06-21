from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import assessment_dict, message_dict
from ..database import get_db
from ..models import RawMessage, RiskAssessment, RiskReason, UnifiedMessage
from ..services.audit_logger import log_action
from ..services.priority_engine import assess_message
from ..services.user_rule_engine import load_enabled_rules

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("")
def list_messages(
    platform: str | None = None,
    priority: str | None = None,
    action_needed: bool | None = None,
    account_id: str | None = None,
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(UnifiedMessage).join(RiskAssessment, RiskAssessment.message_id == UnifiedMessage.id)
    if platform:
        stmt = stmt.where(UnifiedMessage.platform == platform)
    if priority:
        stmt = stmt.where(RiskAssessment.priority_level == priority)
    if action_needed is not None:
        stmt = stmt.where(RiskAssessment.action_score >= 30 if action_needed else RiskAssessment.action_score < 30)
    if account_id:
        stmt = stmt.where(UnifiedMessage.connected_account_id == account_id)
    messages = db.scalars(stmt.order_by(UnifiedMessage.received_at.desc()).limit(limit)).all()
    return [message_dict(db, item) for item in messages]


@router.get("/{message_id}")
def get_message(message_id: str, db: Session = Depends(get_db)):
    message = db.get(UnifiedMessage, message_id)
    if not message:
        raise HTTPException(404, "Message not found")
    return message_dict(db, message, include_detail=True)


@router.get("/{message_id}/assessment")
def get_assessment(message_id: str, db: Session = Depends(get_db)):
    assessment = db.scalar(select(RiskAssessment).where(RiskAssessment.message_id == message_id))
    if not assessment:
        raise HTTPException(404, "Assessment not found")
    return assessment_dict(db, assessment)


@router.post("/{message_id}/reanalyze")
def reanalyze(message_id: str, db: Session = Depends(get_db)):
    message = db.get(UnifiedMessage, message_id)
    assessment = db.scalar(select(RiskAssessment).where(RiskAssessment.message_id == message_id))
    raw = db.get(RawMessage, f"raw_{message_id}")
    if not message or not assessment:
        raise HTTPException(404, "Message not found")
    category = json.loads(raw.raw_payload_json).get("category", "") if raw else ""
    data = assess_message(
        {
            "subject": message.subject,
            "body_text": message.body_text,
            "sender_name": message.sender_name,
            "sender_identifier": message.sender_identifier,
            "category": category,
        },
        user_rules=load_enabled_rules(db),
    )
    before = {"priority": assessment.priority_level, "score": assessment.priority_score}
    for key in ["urgency_score", "risk_score", "action_score", "priority_score", "priority_level", "recommended_action", "summary"]:
        setattr(assessment, key, data[key])
    db.query(RiskReason).filter(RiskReason.assessment_id == assessment.id).delete()
    for reason in data["reasons"]:
        db.add(RiskReason(id=f"reason_{uuid.uuid4().hex[:12]}", assessment_id=assessment.id, **reason))
    log_action(db, "Risk Engine", "Reanalyzed message", "message", message_id, before, {"priority": assessment.priority_level, "score": assessment.priority_score})
    db.commit()
    return assessment_dict(db, assessment)
