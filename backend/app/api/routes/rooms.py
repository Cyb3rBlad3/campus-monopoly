from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.game import CreateRoomRequest, JoinPlayerRequest, StartRoomRequest
from app.services.game_service import GameService


router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("")
def list_rooms(
    status: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return GameService(db).list_rooms(status=status, limit=limit)


@router.post("")
def create_room(body: CreateRoomRequest | None = None, db: Session = Depends(get_db)):
    payload = body or CreateRoomRequest()
    return GameService(db).create_room(payload)


@router.post("/{room_id}/presence")
def touch_presence(
    room_id: str,
    body: JoinPlayerRequest,
    db: Session = Depends(get_db),
):
    return GameService(db).touch_presence(room_id, body)


@router.post("/{room_id}/rejoin")
def rejoin_room(
    room_id: str,
    body: JoinPlayerRequest,
    db: Session = Depends(get_db),
):
    return GameService(db).rejoin_room(room_id, body)


@router.post("/{room_id}/players")
def join_room(
    room_id: str,
    body: JoinPlayerRequest,
    db: Session = Depends(get_db),
):
    return GameService(db).join_room(room_id, body)


@router.post("/{room_id}/start")
def start_room(
    room_id: str,
    body: StartRoomRequest,
    db: Session = Depends(get_db),
):
    return GameService(db).start_room(room_id, body)
