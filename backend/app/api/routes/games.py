from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.game import EndTurnRequest, RollRequest, TileActionRequest, UseCardRequest
from app.services.game_service import GameService


router = APIRouter(prefix="/api/games", tags=["games"])


@router.get("/{game_id}")
def get_game(game_id: str, db: Session = Depends(get_db)):
    return GameService(db).get_game(game_id)


@router.post("/{game_id}/roll")
def roll(game_id: str, body: RollRequest, db: Session = Depends(get_db)):
    return GameService(db).roll(game_id, body)


@router.post("/{game_id}/tile-action")
def tile_action(game_id: str, body: TileActionRequest, db: Session = Depends(get_db)):
    return GameService(db).tile_action(game_id, body)


@router.post("/{game_id}/use-card")
def use_card(game_id: str, body: UseCardRequest, db: Session = Depends(get_db)):
    return GameService(db).use_card(game_id, body)


@router.post("/{game_id}/end-turn")
def end_turn(game_id: str, body: EndTurnRequest, db: Session = Depends(get_db)):
    return GameService(db).end_turn(game_id, body)
