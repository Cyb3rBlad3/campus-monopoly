from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import GameModel, RoomModel, RoomPlayerModel
from app.domain import rules
from app.schemas.game import (
    CreateRoomRequest,
    EndTurnRequest,
    JoinPlayerRequest,
    RollRequest,
    TileActionRequest,
    UseCardRequest,
)


class GameService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_room(self, body: CreateRoomRequest) -> dict:
        room_id = f"room_{uuid4().hex[:8]}"
        game_id = f"game_{uuid4().hex[:8]}"
        state = rules.create_waiting_state(
            game_id=game_id,
            room_id=room_id,
            max_players=body.maxPlayers,
            initial_allowance=body.initialAllowance,
        )

        self.db.add(
            RoomModel(
                id=room_id,
                max_players=body.maxPlayers,
                initial_allowance=body.initialAllowance,
                status="waiting",
            )
        )
        self.db.add(GameModel(id=game_id, room_id=room_id, status="waiting", state_json=state))
        self.db.commit()
        return deepcopy(state)

    def join_room(self, room_id: str, body: JoinPlayerRequest) -> dict:
        room = self._get_room(room_id)
        if room.status != "waiting":
            raise AppError("房间已经开局，不能加入", 409)

        existing_players = self._room_players(room_id)
        if len(existing_players) >= room.max_players:
            raise AppError("房间人数已满", 400)

        joined_order = len(existing_players) + 1
        player_id = f"{room_id}_p{joined_order}"
        self.db.add(
            RoomPlayerModel(
                id=player_id,
                room_id=room_id,
                name=body.name,
                avatar_id=body.avatarId,
                piece_color=body.pieceColor,
                saving_goal_type=body.savingGoalType,
                joined_order=joined_order,
            )
        )

        game = self._get_game_by_room(room_id)
        room_players = existing_players + [
            RoomPlayerModel(
                id=player_id,
                room_id=room_id,
                name=body.name,
                avatar_id=body.avatarId,
                piece_color=body.pieceColor,
                saving_goal_type=body.savingGoalType,
                joined_order=joined_order,
            )
        ]
        players = self._players_from_room_players(room, room_players)
        game.state_json = rules.sync_waiting_players(game.state_json, players)
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return self._mutation_response(game.state_json, None)

    def start_room(self, room_id: str) -> dict:
        room = self._get_room(room_id)
        if room.status != "waiting":
            raise AppError("房间已经开局", 409)

        room_players = self._room_players(room_id)
        if len(room_players) < 2:
            raise AppError("至少需要 2 名玩家才能开局", 400)

        game = self._get_game_by_room(room_id)
        players = self._players_from_room_players(room, room_players)
        game.state_json = rules.start_game_from_players(game.state_json, players)
        game.status = "playing"
        room.status = "playing"
        self.db.add_all([room, game])
        self.db.commit()
        self.db.refresh(game)
        return self._mutation_response(game.state_json, None)

    def get_game(self, game_id: str) -> dict:
        return deepcopy(self._get_game(game_id).state_json)

    def roll(self, game_id: str, body: RollRequest) -> dict:
        game = self._get_game(game_id)
        next_state, turn_result = rules.roll(
            game.state_json,
            player_id=body.playerId,
            dice=body.dice,
        )
        return self._save_mutation(game, next_state, turn_result)

    def tile_action(self, game_id: str, body: TileActionRequest) -> dict:
        game = self._get_game(game_id)
        next_state, turn_result = rules.tile_action(
            game.state_json,
            player_id=body.playerId,
            action=body.action,
            target_player_id=body.targetPlayerId,
            amount=body.amount,
        )
        return self._save_mutation(game, next_state, turn_result)

    def use_card(self, game_id: str, body: UseCardRequest) -> dict:
        game = self._get_game(game_id)
        next_state, turn_result = rules.use_card(
            game.state_json,
            player_id=body.playerId,
            card_id=body.cardId,
            target_player_id=body.targetPlayerId,
        )
        return self._save_mutation(game, next_state, turn_result)

    def end_turn(self, game_id: str, body: EndTurnRequest) -> dict:
        game = self._get_game(game_id)
        next_state, turn_result = rules.end_turn(game.state_json, player_id=body.playerId)
        return self._save_mutation(game, next_state, turn_result)

    def _save_mutation(
        self,
        game: GameModel,
        state: dict,
        turn_result: dict | None,
    ) -> dict:
        game.state_json = state
        game.status = state["status"]
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return self._mutation_response(game.state_json, turn_result)

    def _get_room(self, room_id: str) -> RoomModel:
        room = self.db.get(RoomModel, room_id)
        if room is None:
            raise AppError("房间不存在", 404)
        return room

    def _get_game(self, game_id: str) -> GameModel:
        game = self.db.get(GameModel, game_id)
        if game is None:
            raise AppError("游戏不存在", 404)
        return game

    def _get_game_by_room(self, room_id: str) -> GameModel:
        game = self.db.scalar(select(GameModel).where(GameModel.room_id == room_id))
        if game is None:
            raise AppError("房间对应的游戏不存在", 404)
        return game

    def _room_players(self, room_id: str) -> list[RoomPlayerModel]:
        return list(
            self.db.scalars(
                select(RoomPlayerModel)
                .where(RoomPlayerModel.room_id == room_id)
                .order_by(RoomPlayerModel.joined_order)
            )
        )

    def _players_from_room_players(
        self,
        room: RoomModel,
        room_players: list[RoomPlayerModel],
    ) -> list[dict]:
        return [
            rules.make_player(
                player_id=player.id,
                name=player.name,
                avatar_id=player.avatar_id,
                piece_color=player.piece_color,
                saving_goal_type=player.saving_goal_type,
                initial_allowance=room.initial_allowance,
            )
            for player in sorted(room_players, key=lambda p: p.joined_order)
        ]

    @staticmethod
    def _mutation_response(game_state: dict, turn_result: dict | None) -> dict:
        return {"gameState": deepcopy(game_state), "turnResult": deepcopy(turn_result)}
