from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import message_dict
from ..database import get_db
from ..models import NotificationEvent, RiskAssessment, UnifiedMessage, UserActionItem
from ..services.audit_logger import log_action

router = APIRouter(prefix="/api/triage", tags=["triage"])


@router.get("")
def triage_queue(db: Session = Depends(get_db)):
    messages = db.scalars(
        select(UnifiedMessage)
        .join(RiskAssessment)
        .where(RiskAssessment.priority_level.in_(["P0_IMMEDIATE", "P1_TODAY"]))
        .order_by(RiskAssessment.priority_score.desc())
    ).all()
    return [message_dict(db, item) for item in messages]


@router.get("/{message_id}")
def triage_detail(message_id: str, db: Session = Depends(get_db)):
    message = db.get(UnifiedMessage, message_id)
    if not message:
        raise HTTPException(404, "Message not found")
    return message_dict(db, message, include_detail=True)


def _message(db: Session, message_id: str) -> UnifiedMessage:
    item = db.get(UnifiedMessage, message_id)
    if not item:
        raise HTTPException(404, "Message not found")
    return item


@router.post("/{message_id}/mark-action-needed")
def mark_action_needed(message_id: str, db: Session = Depends(get_db)):
    message = _message(db, message_id)
    task = UserActionItem(id=f"task_{uuid.uuid4().hex[:10]}", message_id=message.id, title=f"Action needed: {message.subject or message.sender_name}", description=message.body_text[:240], source_platform=message.platform)
    db.add(task)
    log_action(db, "User", "Marked action needed", "message", message_id, after={"task_id": task.id})
    db.commit()
    return {"status": "created", "task_id": task.id}


@router.post("/{message_id}/create-task")
def create_task(message_id: str, db: Session = Depends(get_db)):
    return mark_action_needed(message_id, db)


@router.post("/{message_id}/send-to-scheduling-review")
def scheduling_review(message_id: str, db: Session = Depends(get_db)):
    _message(db, message_id)
    log_action(db, "User", "Sent to scheduling review", "message", message_id, after={"queue": "TrustOps scheduling review"})
    db.commit()
    return {"status": "queued", "queue": "TrustOps scheduling review"}


@router.post("/{message_id}/mark-safe")
def mark_safe(message_id: str, db: Session = Depends(get_db)):
    _message(db, message_id)
    notifications = db.scalars(select(NotificationEvent).where(NotificationEvent.message_id == message_id)).all()
    for notification in notifications:
        notification.status = "resolved"
    log_action(db, "User", "Marked not important", "message", message_id, after={"notifications_resolved": len(notifications)})
    db.commit()
    return {"status": "safe", "notifications_resolved": len(notifications)}

