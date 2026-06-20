from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.evaluation_service import run_evaluation

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])
LATEST: dict | None = None


@router.post("/run")
def evaluate(db: Session = Depends(get_db)):
    global LATEST
    LATEST = run_evaluation(db)
    return LATEST


@router.get("/latest")
def latest(db: Session = Depends(get_db)):
    global LATEST
    if LATEST is None:
        LATEST = run_evaluation(db, write_report=False)
    return LATEST
