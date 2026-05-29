from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc_aware(dt: datetime) -> datetime:
    """SQLite 读回的 datetime 常为 naive，统一为 UTC aware 再比较。"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class Base(DeclarativeBase):
    pass


class RoomModel(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    max_players: Mapped[int] = mapped_column(Integer, default=4)
    initial_allowance: Mapped[int] = mapped_column(Integer, default=2000)
    status: Mapped[str] = mapped_column(String(32), default="waiting")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class RoomPlayerModel(Base):
    __tablename__ = "room_players"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    avatar_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    piece_color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    saving_goal_type: Mapped[str] = mapped_column(String(32), default="standard")
    joined_order: Mapped[int] = mapped_column(Integer)
    device_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class GameModel(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="waiting")
    state_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
