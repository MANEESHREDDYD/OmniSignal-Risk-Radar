from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import notification_dict
from ..database import get_db
from ..models import NotificationEvent, now_iso
from ..services.audit_logger import log_action

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class SnoozeBody(BaseModel):
    until: str | None = None
    hours: int = 2


@router.get("")
def list_notifications(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(NotificationEvent)
    if status:
        stmt = stmt.where(NotificationEvent.status == status)
    notifications = db.scalars(stmt.order_by(NotificationEvent.created_at.desc())).all()
    return [notification_dict(db, item) for item in notifications]


def _mutate(notification_id: str, status: str, db: Session, extra: dict | None = None):
    item = db.get(NotificationEvent, notification_id)
    if not item:
        raise HTTPException(404, "Notification not found")
    before = {"status": item.status}
    item.status = status
    if status == "dismissed":
        item.dismissed_at = now_iso()
    for key, value in (extra or {}).items():
        setattr(item, key, value)
    log_action(db, "User", f"{status.title()} notification", "notification", notification_id, before, {"status": status, **(extra or {})})
    db.commit()
    return notification_dict(db, item)


@router.post("/{notification_id}/dismiss")
def dismiss(notification_id: str, db: Session = Depends(get_db)):
    return _mutate(notification_id, "dismissed", db)


@router.post("/{notification_id}/snooze")
def snooze(notification_id: str, body: SnoozeBody, db: Session = Depends(get_db)):
    until = body.until or (datetime.now().astimezone() + timedelta(hours=body.hours)).isoformat()
    return _mutate(notification_id, "snoozed", db, {"snoozed_until": until})


@router.post("/{notification_id}/resolve")
def resolve(notification_id: str, db: Session = Depends(get_db)):
    return _mutate(notification_id, "resolved", db)

