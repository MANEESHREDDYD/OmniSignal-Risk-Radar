"""Google OAuth routes (read-only). All real flows are guarded.

When real connectors are disabled, the guarded endpoints return a safe, audited
"blocked" response instead of crashing. The status endpoint always works.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import GOOGLE_READONLY_SCOPES, settings
from ..database import get_db
from ..models import ConnectedAccount, EncryptedToken, OAuthConnection, now_iso
from ..services import google_oauth
from ..services.audit_logger import log_action
from ..services.oauth_token_service import (
    delete_tokens,
    expiry_from_seconds,
    store_tokens,
)
from ..services.real_connector_guard import (
    MissingConnectorConfigError,
    RealConnectorsDisabledError,
    ensure_google_configured,
)
from ..services.real_ingestion_service import delete_real_cache

router = APIRouter(prefix="/api/auth/google", tags=["auth_google"])

OAUTH_STATE_TTL_MINUTES = 10
# Local-dev, single-process state store. Production should use durable,
# server-side session storage shared across workers.
_pending_states: dict[str, dict[str, str]] = {}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _create_oauth_state(now: datetime | None = None) -> str:
    current = now or _utc_now()
    for existing_state, record in list(_pending_states.items()):
        if datetime.fromisoformat(record["expires_at"]) <= current:
            _pending_states.pop(existing_state, None)
    state = secrets.token_urlsafe(24)
    _pending_states[state] = {
        "created_at": current.isoformat(),
        "expires_at": (
            current + timedelta(minutes=OAUTH_STATE_TTL_MINUTES)
        ).isoformat(),
    }
    return state


def _consume_oauth_state(state: str, now: datetime | None = None) -> str:
    if not state:
        return "missing"
    record = _pending_states.pop(state, None)
    if not record:
        return "unknown"
    current = now or _utc_now()
    expires_at = datetime.fromisoformat(record["expires_at"])
    return "expired" if expires_at <= current else "valid"


def _blocked(db: Session, action: str, error: Exception) -> JSONResponse:
    status = getattr(error, "status", "blocked")
    message = getattr(error, "message", str(error))
    log_action(
        db,
        "Real Connector Guard",
        f"Blocked {action}",
        "real_connector",
        "google",
        after={"status": status},  # no secrets
    )
    db.commit()
    return JSONResponse(
        status_code=200,
        content={
            "status": status,
            "real_connectors_enabled": settings.REAL_CONNECTORS_ENABLED,
            "message": message,
        },
    )


def _connection_dict(db: Session, conn: OAuthConnection) -> dict:
    import json

    has_tokens = db.scalar(
        select(EncryptedToken).where(EncryptedToken.oauth_connection_id == conn.id)
    ) is not None
    return {
        "id": conn.id,
        "provider": conn.provider,
        "account_email": conn.account_email,
        "display_name": conn.display_name,
        "status": conn.status,
        "is_read_only": conn.is_read_only,
        "scopes": json.loads(conn.scopes_json or "[]"),
        "connected_at": conn.connected_at,
        "disconnected_at": conn.disconnected_at,
        "last_sync_at": conn.last_sync_at,
        "has_stored_tokens": has_tokens,  # boolean only — never the token itself
    }


@router.get("/status")
def google_status(db: Session = Depends(get_db)):
    """Always available — never exposes secrets."""
    connections = db.scalars(
        select(OAuthConnection).where(OAuthConnection.provider == "google").order_by(OAuthConnection.created_at)
    ).all()
    return {
        "real_connectors_enabled": settings.REAL_CONNECTORS_ENABLED,
        "google_configured": settings.google_oauth_configured,
        "token_encryption_configured": settings.token_encryption_configured,
        "scopes": GOOGLE_READONLY_SCOPES,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "connections": [_connection_dict(db, c) for c in connections],
    }


@router.get("/start")
def google_start(db: Session = Depends(get_db)):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "Google OAuth start", error)

    state = _create_oauth_state()
    url = google_oauth.build_authorization_url(state)
    log_action(db, "Real Connector", "Started Google OAuth", "real_connector", "google", after={"scopes": GOOGLE_READONLY_SCOPES})
    db.commit()
    return {"authorization_url": url, "state": state}


@router.get("/callback")
def google_callback(
    code: str = Query(default=""),
    state: str = Query(default=""),
    db: Session = Depends(get_db),
):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "Google OAuth callback", error)

    frontend = settings.FRONTEND_ORIGIN.rstrip("/")
    state_status = _consume_oauth_state(state)
    if state_status != "valid":
        log_action(
            db,
            "Real Connector",
            "Rejected Google callback (bad state)",
            "real_connector",
            "google",
            after={"state_status": state_status},
        )
        db.commit()
        suffix = "error_state_expired" if state_status == "expired" else "error_state"
        return RedirectResponse(url=f"{frontend}/settings/integrations?google={suffix}")

    try:
        token_payload = google_oauth.exchange_code(code)
    except Exception:  # network/exchange failure — never leak details
        log_action(db, "Real Connector", "Google token exchange failed", "real_connector", "google", after={"status": "error"})
        db.commit()
        return RedirectResponse(url=f"{frontend}/settings/integrations?google=error_exchange")

    access_token = token_payload.get("access_token")
    refresh_token = token_payload.get("refresh_token")
    userinfo = google_oauth.fetch_userinfo(access_token) if access_token else {}
    email = userinfo.get("email")
    display_name = userinfo.get("name")

    import json

    connection_id = f"oauth_{uuid.uuid4().hex[:12]}"
    account_id = f"acct_{uuid.uuid4().hex[:12]}"
    db.add(
        ConnectedAccount(
            id=account_id,
            user_id="user_001",
            platform="google",
            account_label=f"Google · {email or 'connected account'}",
            account_identifier=email or "google-account",
            connection_status="connected",
            is_demo=False,
            last_sync_at=None,
        )
    )
    connection = OAuthConnection(
        id=connection_id,
        user_id="user_001",
        provider="google",
        account_email=email,
        display_name=display_name,
        scopes_json=json.dumps(GOOGLE_READONLY_SCOPES),
        status="connected",
        is_read_only=True,
        connected_account_id=account_id,
        connected_at=now_iso(),
        updated_at=now_iso(),
    )
    db.add(connection)
    store_tokens(
        db,
        oauth_connection_id=connection_id,
        provider="google",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=token_payload.get("token_type"),
        expires_at=expiry_from_seconds(token_payload.get("expires_in")),
        scopes=GOOGLE_READONLY_SCOPES,
    )
    log_action(
        db,
        "Real Connector",
        "Connected Google account",
        "oauth_connection",
        connection_id,
        after={"account_email": email, "read_only": True},
    )
    db.commit()
    return RedirectResponse(url=f"{frontend}/settings/integrations?google=connected")


@router.post("/disconnect/{connection_id}")
def google_disconnect(connection_id: str, db: Session = Depends(get_db)):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "Google disconnect", error)

    connection = db.get(OAuthConnection, connection_id)
    if not connection:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "Connection not found."})

    removed = delete_tokens(db, connection_id)
    connection.status = "disconnected"
    connection.disconnected_at = now_iso()
    connection.updated_at = now_iso()
    if connection.connected_account_id:
        account = db.get(ConnectedAccount, connection.connected_account_id)
        if account:
            account.connection_status = "disconnected"
    log_action(
        db,
        "Real Connector",
        "Disconnected Google account",
        "oauth_connection",
        connection_id,
        after={"tokens_deleted": removed},
    )
    db.commit()
    return {"status": "disconnected", "connection_id": connection_id, "tokens_deleted": removed}


@router.post("/delete-cache/{connection_id}")
def google_delete_cache(connection_id: str, db: Session = Depends(get_db)):
    try:
        ensure_google_configured()
    except (RealConnectorsDisabledError, MissingConnectorConfigError) as error:
        return _blocked(db, "Google delete-cache", error)

    connection = db.get(OAuthConnection, connection_id)
    if not connection:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "Connection not found."})

    counts = delete_real_cache(db, connection)
    log_action(
        db,
        "Real Connector",
        "Deleted local real cache",
        "oauth_connection",
        connection_id,
        after=counts,
    )
    db.commit()
    return {"status": "cache_deleted", "connection_id": connection_id, **counts}
