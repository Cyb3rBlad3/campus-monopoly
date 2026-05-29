from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


engine = None
SessionLocal: sessionmaker[Session] | None = None


def _sqlite_path_from_url(database_url: str) -> Path | None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return None
    raw_path = database_url.removeprefix(prefix)
    if raw_path == ":memory:":
        return None
    return Path(raw_path)


def configure_engine(database_url: str | None = None) -> None:
    global engine, SessionLocal
    if engine is not None:
        engine.dispose()

    url = database_url or get_settings().database_url
    sqlite_path = _sqlite_path_from_url(url)
    if sqlite_path is not None:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from app.db.models import Base

    if engine is None:
        configure_engine()
    Base.metadata.create_all(bind=engine)


def get_db():
    if SessionLocal is None:
        configure_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


configure_engine()
