from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ConnectedAccount, RawMessage, SyncRun, now_iso
from ..seed import seed_database
from ..services.audit_logger import log_action

router = APIRouter(prefix="/api/connections", tags=["connections"])


@router.get("")
def list_connections(db: Session = Depends(get_db)):
    accounts = db.scalars(select(ConnectedAccount).order_by(ConnectedAccount.created_at)).all()
    return [
        {
            "id": account.id,
            "platform": account.platform,
            "account_label": account.account_label,
            "account_identifier": account.account_identifier,
            "connection_status": account.connection_status,
            "is_demo": account.is_demo,
            "last_sync_at": account.last_sync_at,
            "messages_synced": db.scalar(select(func.count()).select_from(RawMessage).where(RawMessage.connected_account_id == account.id)) or 0,
        }
        for account in accounts
    ]


@router.post("/demo-seed")
def demo_seed(force: bool = False, db: Session = Depends(get_db)):
    return seed_database(db, force=force)


@router.post("/{account_id}/sync")
def sync_account(account_id: str, db: Session = Depends(get_db)):
    account = db.get(ConnectedAccount, account_id)
    if not account:
        raise HTTPException(404, "Connected account not found")
    count = db.scalar(select(func.count()).select_from(RawMessage).where(RawMessage.connected_account_id == account_id)) or 0
    run = SyncRun(
        id=f"sync_{uuid.uuid4().hex[:10]}",
        connected_account_id=account_id,
        status="completed",
        messages_seen=count,
        messages_created=0,
        messages_updated=0,
        completed_at=now_iso(),
    )
    account.last_sync_at = now_iso()
    db.add(run)
    log_action(db, "Ingestion Service", "Synced demo account", "connected_account", account_id, after={"messages_seen": count})
    db.commit()
    return {"sync_run_id": run.id, "status": run.status, "messages_seen": count, "messages_created": 0}

