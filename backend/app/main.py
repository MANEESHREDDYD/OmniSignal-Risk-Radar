from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import analytics, audit, connections, evaluation, inbox, messages, notifications, radar, rules, triage
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        with SessionLocal() as db:
            seed_database(db)
    yield


app = FastAPI(
    title="OmniSignal Risk Radar API",
    description="Local-first cross-platform message intelligence for AI secretary products.",
    version="1.0.0",
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
]:
    app.include_router(router)


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo", "paid_apis": False}
