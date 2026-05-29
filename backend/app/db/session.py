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


def _sqlite_add_column_if_missing(table: str, column: str, ddl: str) -> None:
    if engine is None:
        return
    url = str(engine.url)
    if not url.startswith("sqlite"):
        return
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
        names = {row[1] for row in rows}
        if column not in names:
            conn.exec_driver_sql(ddl)
            conn.commit()


def init_db() -> None:
    from app.db.models import Base

    if engine is None:
        configure_engine()
    Base.metadata.create_all(bind=engine)
    _sqlite_add_column_if_missing(
        "room_players",
        "device_id",
        "ALTER TABLE room_players ADD COLUMN device_id VARCHAR(128)",
    )
    _sqlite_add_column_if_missing(
        "room_players",
        "last_seen_at",
        "ALTER TABLE room_players ADD COLUMN last_seen_at DATETIME",
    )


def get_db():
    if SessionLocal is None:
        configure_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


configure_engine()
