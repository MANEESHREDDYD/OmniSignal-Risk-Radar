"""Real read-only sync routes. All sync flows are guarded.

These pull a small, safe batch of Gmail messages and Calendar events read-only,
run them through the existing scoring/notification pipeline, and never perform any
outbound or write action.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import OAuthConnection, ProviderMessageCursor, RealSyncRun, now_iso
from ..services.audit_logger import log_action
from ..services.connectors.google_calendar_connector import GoogleCalendarConnector
from ..services.connectors.google_gmail_connector import GoogleGmailConnector
from ..services.google_api_client import CalendarHttpClient, GmailHttpClient
from ..services.oauth_token_service import get_decrypted_tokens
from ..services.real_connector_guard import (
    MissingConnectorConfigError,
    RealConnectorsDisabledError,
    ensure_google_configured,
)
from ..services.real_ingestion_service import ingest_real_items

router = APIRouter(prefix="/api/real-sync", tags=["real_sync"])


def _uid() -> str:
    return f"realsync_{uuid.uuid4().hex[:10]}"


def _blocked(db: Session, sync_type: str, connection_id: str, error: Exception) -> JSONResponse:
    status = getattr(error, "status", "blocked")
    message = getattr(error, "message", str(error))
    run = RealSyncRun(
        id=_uid(),
        oauth_connection_id=connection_id,
        provider="google",
        sync_type=sync_type,
        status=status,
        started_at=now_iso(),
        completed_at=now_iso(),
        error_message=message,
    )
    db.add(run)
    log_action(db, "Real Connector Guard", f"Blocked real sync ({sync_type})", "oauth_connection", connection_id, after={"status": status})
    db.commit()
    return JSONResponse(status_code=200, content={"status": status, "message": message, "sync_run_id": run.id})


def _require_connected(db: Session, connection_id: str) -> OAuthConnection | None:
    connection = db.get(OAuthConnection, connection_id)
    if not connection or connection.status != "connected":
        return None
    return connection


def _update_cursor(db: Session, connection: OAuthConnection, resource_type: str) -> None:
    cursor = db.scalar(
        select(ProviderMessageCursor).where(
            ProviderMessageCursor.oauth_connection_id == connection.id,
            ProviderMessageCursor.resource_type == resource_type,
        )
    )
    if cursor:
        cursor.last_seen_at = now_iso()
        cursor.updated_at = now_iso()
    else:
        db.add(
            ProviderMessageCursor(
                id=f"cursor_{uuid.uuid4().hex[:10]}",
                oauth_connection_id=connection.id,
                provider=connection.provider,
                resource_type=resource_type,
                cursor_value=None,
                last_seen_at=now_iso(),
            )
        )


def _run_gmail(db: Session, connection: OAuthConnection) -> dict:
    tokens = get_decrypted_tokens(db, connection.id)
    client = GmailHttpClient(tokens["access_token"])
    connector = GoogleGmailConnector(client)
    items = connector.fetch_normalized(connection.connected_account_id, max_results=25)
    counts = ingest_real_items(db, connection=connection, connected_account_id=connection.connected_account_id, items=items)
    _update_cursor(db, connection, "gmail_messages")
    return counts


def _run_calendar(db: Session, connection: OAuthConnection) -> dict:
    tokens = get_decrypted_tokens(db, connection.id)
    client = CalendarHttpClient(tokens["access_token"])
    connector = GoogleCalendarConnector(client)
    items = connector.fetch_normalized(connection.connected_account_id, max_results=25)
    counts = ingest_real_items(db, connection=connection, connected_account_id=connection.connected_account_id, items=items)
    _update_cursor(db, connection, "calendar_events")
    return counts


@router.post("/google/{connection_id}/gmail")
def sync_gmail(connection_id: str, db: Session = Depends(get_db)):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "gmail_messages", connection_id, error)

    connection = _require_connected(db, connection_id)
    if not connection:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "No connected Google account."})

    run = RealSyncRun(id=_uid(), oauth_connection_id=connection_id, provider="google", sync_type="gmail_messages", status="running", started_at=now_iso())
    db.add(run)
    db.flush()
    try:
        counts = _run_gmail(db, connection)
    except Exception as exc:  # safe failure path
        run.status = "failed"
        run.completed_at = now_iso()
        run.error_message = type(exc).__name__
        log_action(db, "Real Connector", "Gmail sync failed", "oauth_connection", connection_id, after={"error": type(exc).__name__})
        db.commit()
        return JSONResponse(status_code=200, content={"status": "failed", "sync_run_id": run.id})

    run.status = "completed"
    run.messages_seen = counts["seen"]
    run.messages_created = counts["created"]
    run.completed_at = now_iso()
    connection.last_sync_at = now_iso()
    log_action(db, "Real Connector", "Synced Gmail (read-only)", "oauth_connection", connection_id, after=counts)
    db.commit()
    return {"status": "completed", "sync_run_id": run.id, **counts}


@router.post("/google/{connection_id}/calendar")
def sync_calendar(connection_id: str, db: Session = Depends(get_db)):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "calendar_events", connection_id, error)

    connection = _require_connected(db, connection_id)
    if not connection:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "No connected Google account."})

    run = RealSyncRun(id=_uid(), oauth_connection_id=connection_id, provider="google", sync_type="calendar_events", status="running", started_at=now_iso())
    db.add(run)
    db.flush()
    try:
        counts = _run_calendar(db, connection)
    except Exception as exc:
        run.status = "failed"
        run.completed_at = now_iso()
        run.error_message = type(exc).__name__
        log_action(db, "Real Connector", "Calendar sync failed", "oauth_connection", connection_id, after={"error": type(exc).__name__})
        db.commit()
        return JSONResponse(status_code=200, content={"status": "failed", "sync_run_id": run.id})

    run.status = "completed"
    run.calendar_events_seen = counts["seen"]
    run.calendar_events_created = counts["created"]
    run.completed_at = now_iso()
    connection.last_sync_at = now_iso()
    log_action(db, "Real Connector", "Synced Calendar (read-only)", "oauth_connection", connection_id, after=counts)
    db.commit()
    return {"status": "completed", "sync_run_id": run.id, **counts}


@router.post("/google/{connection_id}/full-readonly")
def sync_full(connection_id: str, db: Session = Depends(get_db)):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "full_google_readonly", connection_id, error)

    connection = _require_connected(db, connection_id)
    if not connection:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "No connected Google account."})

    run = RealSyncRun(id=_uid(), oauth_connection_id=connection_id, provider="google", sync_type="full_google_readonly", status="running", started_at=now_iso())
    db.add(run)
    db.flush()
    try:
        gmail_counts = _run_gmail(db, connection)
        calendar_counts = _run_calendar(db, connection)
    except Exception as exc:
        run.status = "failed"
        run.completed_at = now_iso()
        run.error_message = type(exc).__name__
        log_action(db, "Real Connector", "Full Google sync failed", "oauth_connection", connection_id, after={"error": type(exc).__name__})
        db.commit()
        return JSONResponse(status_code=200, content={"status": "failed", "sync_run_id": run.id})

    run.status = "completed"
    run.messages_seen = gmail_counts["seen"]
    run.messages_created = gmail_counts["created"]
    run.calendar_events_seen = calendar_counts["seen"]
    run.calendar_events_created = calendar_counts["created"]
    run.completed_at = now_iso()
    connection.last_sync_at = now_iso()
    log_action(db, "Real Connector", "Full Google read-only sync", "oauth_connection", connection_id, after={"gmail": gmail_counts, "calendar": calendar_counts})
    db.commit()
    return {"status": "completed", "sync_run_id": run.id, "gmail": gmail_counts, "calendar": calendar_counts}


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.scalars(select(RealSyncRun).order_by(RealSyncRun.started_at.desc()).limit(50)).all()
    return [
        {
            "id": run.id,
            "oauth_connection_id": run.oauth_connection_id,
            "provider": run.provider,
            "sync_type": run.sync_type,
            "status": run.status,
            "messages_seen": run.messages_seen,
            "messages_created": run.messages_created,
            "calendar_events_seen": run.calendar_events_seen,
            "calendar_events_created": run.calendar_events_created,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "error_message": run.error_message,
        }
        for run in runs
    ]
