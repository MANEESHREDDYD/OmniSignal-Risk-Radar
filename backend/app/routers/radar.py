from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..api_utils import message_dict
from ..database import get_db
from ..models import ConnectedAccount, RiskAssessment, RiskReason, UnifiedMessage

router = APIRouter(prefix="/api/radar", tags=["radar"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    assessments = db.scalars(select(RiskAssessment)).all()
    reason_codes = [item.reason_code for item in db.scalars(select(RiskReason)).all()]
    counts = Counter(item.priority_level for item in assessments)
    return {
        "immediate_alerts": counts["P0_IMMEDIATE"],
        "attention_today": counts["P1_TODAY"],
        "action_needed": sum(item.action_score >= 30 for item in assessments),
        "scheduling_risks": sum(code in {"scheduling_request", "reschedule_request", "calendar_conflict", "timezone_unclear"} for code in reason_codes),
        "security_finance_alerts": sum(code in {"security_alert", "financial_risk"} for code in reason_codes),
        "deadlines_soon": sum(code in {"deadline_today", "deadline_tomorrow", "deadline_soon"} for code in reason_codes),
        "accounts_monitored": db.scalar(select(func.count()).select_from(ConnectedAccount)) or 0,
        "messages_analyzed": len(assessments),
        "priority_distribution": dict(counts),
    }


@router.get("/high-risk")
def high_risk(db: Session = Depends(get_db)):
    messages = db.scalars(
        select(UnifiedMessage).join(RiskAssessment).where(RiskAssessment.risk_score >= 40).order_by(RiskAssessment.risk_score.desc())
    ).all()
    return [message_dict(db, item) for item in messages]


@router.get("/action-needed")
def action_needed(db: Session = Depends(get_db)):
    messages = db.scalars(
        select(UnifiedMessage).join(RiskAssessment).where(RiskAssessment.action_score >= 30).order_by(RiskAssessment.action_score.desc())
    ).all()
    return [message_dict(db, item) for item in messages]


@router.get("/by-platform")
def by_platform(db: Session = Depends(get_db)):
    rows = db.execute(select(UnifiedMessage.platform, func.count()).group_by(UnifiedMessage.platform)).all()
    return [{"platform": platform, "count": count} for platform, count in rows]


@router.get("/by-reason")
def by_reason(db: Session = Depends(get_db)):
    rows = db.execute(select(RiskReason.reason_code, func.count()).group_by(RiskReason.reason_code).order_by(func.count().desc())).all()
    return [{"reason": reason, "count": count} for reason, count in rows]

