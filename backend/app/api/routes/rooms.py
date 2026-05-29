from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.game import CreateRoomRequest, JoinPlayerRequest, StartRoomRequest
from app.services.game_service import GameService


router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("")
def create_room(body: CreateRoomRequest | None = None, db: Session = Depends(get_db)):
    payload = body or CreateRoomRequest()
    return GameService(db).create_room(payload)


@router.post("/{room_id}/players")
def join_room(
    room_id: str,
    body: JoinPlayerRequest | None = None,
    db: Session = Depends(get_db),
):
    payload = body or JoinPlayerRequest()
    return GameService(db).join_room(room_id, payload)


@router.post("/{room_id}/start")
def start_room(
    room_id: str,
    body: StartRoomRequest | None = None,
    db: Session = Depends(get_db),
):
    _ = body or StartRoomRequest()
    return GameService(db).start_room(room_id)
