"""Shared fixtures for V1.1 real-connector tests.

Uses an isolated in-memory SQLite database so real-connector tests never touch
the demo file DB, and never call Google (clients are mocked).
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def token_key(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", key)
    return key


@pytest.fixture()
def client(db, monkeypatch):
    """FastAPI TestClient bound to the in-memory DB; demo seeding disabled."""
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setenv("DEMO_MODE", "false")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
