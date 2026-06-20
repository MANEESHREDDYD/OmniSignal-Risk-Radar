from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import REPO_ROOT


class Base(DeclarativeBase):
    pass


DEFAULT_DB = Path(__file__).resolve().parents[1] / "omnisignal.db"


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB.as_posix()}")
    relative_prefix = "sqlite:///./"
    if value.startswith(relative_prefix):
        relative_path = value[len(relative_prefix):]
        return f"sqlite:///{(REPO_ROOT / relative_path).resolve().as_posix()}"
    return value


DATABASE_URL = _database_url()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
