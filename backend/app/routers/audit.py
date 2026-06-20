from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import parse_json
from ..database import get_db
from ..models import AuditLog

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
def audit_log(limit: int = Query(200, le=500), db: Session = Depends(get_db)):
    entries = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()
    return [
        {
            "id": item.id,
            "actor": item.actor,
            "action": item.action,
            "target_type": item.target_type,
            "target_id": item.target_id,
            "before": parse_json(item.before_json),
            "after": parse_json(item.after_json),
            "created_at": item.created_at,
        }
        for item in entries
    ]

