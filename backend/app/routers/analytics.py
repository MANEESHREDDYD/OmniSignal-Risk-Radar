from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import RiskAssessment, RiskReason, UnifiedMessage

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    items = db.scalars(select(RiskAssessment)).all()
    counts = Counter(item.priority_level for item in items)
    total = len(items) or 1
    return {
        "messages_analyzed": len(items),
        "p0_alerts": counts["P0_IMMEDIATE"],
        "p1_alerts": counts["P1_TODAY"],
        "p2_digest": counts["P2_DIGEST"],
        "p3_low": counts["P3_LOW"],
        "action_needed_rate": round(sum(item.action_score >= 30 for item in items) / total * 100, 1),
        "average_priority_score": round(sum(item.priority_score for item in items) / total, 1),
    }


@router.get("/priority-distribution")
def priority_distribution(db: Session = Depends(get_db)):
    rows = db.execute(select(RiskAssessment.priority_level, func.count()).group_by(RiskAssessment.priority_level)).all()
    return [{"name": name, "value": count} for name, count in rows]


@router.get("/platform-breakdown")
def platform_breakdown(db: Session = Depends(get_db)):
    rows = db.execute(select(UnifiedMessage.platform, func.count()).group_by(UnifiedMessage.platform)).all()
    return [{"name": name, "value": count} for name, count in rows]


@router.get("/top-risk-reasons")
def top_reasons(db: Session = Depends(get_db)):
    rows = db.execute(select(RiskReason.reason_code, func.count()).group_by(RiskReason.reason_code).order_by(func.count().desc()).limit(10)).all()
    return [{"name": name, "value": count} for name, count in rows]


@router.get("/action-needed-rate")
def action_rate(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(RiskAssessment)) or 1
    count = db.scalar(select(func.count()).select_from(RiskAssessment).where(RiskAssessment.action_score >= 30)) or 0
    return {"action_needed": count, "total": total, "rate": round(count / total, 3)}

