from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import (
    analytics,
    audit,
    auth_google,
    connections,
    evaluation,
    inbox,
    messages,
    notifications,
    radar,
    real_sync,
    rules,
    triage,
)
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Safety: if real connectors are enabled but the token key is missing, warn
    # loudly. We do NOT crash the app — demo mode stays usable; the real OAuth
    # routes themselves block with a clear error until the key is configured.
    if settings.REAL_CONNECTORS_ENABLED and not settings.token_encryption_configured:
        print(
            "[OmniSignal] WARNING: REAL_CONNECTORS_ENABLED=true but "
            "TOKEN_ENCRYPTION_KEY is missing. Real OAuth/token storage is blocked "
            "until you set it. Synthetic demo mode remains active."
        )
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        with SessionLocal() as db:
            seed_database(db)
    yield


app = FastAPI(
    title="OmniSignal Risk Radar API",
    description="Local-first cross-platform message intelligence for AI secretary products.",
    version="1.1.1",
    lifespan=lifespan,
)
configured_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
allowed_origins = list(
    dict.fromkeys(
        [
            configured_origin,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    connections.router,
    messages.router,
    inbox.router,
    radar.router,
    notifications.router,
    triage.router,
    rules.router,
    analytics.router,
    audit.router,
    evaluation.router,
    auth_google.router,
    real_sync.router,
]:
    app.include_router(router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "1.1.1",
        "demo_mode": settings.DEMO_MODE,
        "real_connectors_enabled": settings.REAL_CONNECTORS_ENABLED,
        "paid_apis": False,
    }
