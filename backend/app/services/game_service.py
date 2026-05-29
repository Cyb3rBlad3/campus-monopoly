from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.room_policy import (
    PLAYER_PRESENCE_TTL_SECONDS,
    WAITING_ROOM_TTL_SECONDS,
)
from app.db.models import GameModel, RoomModel, RoomPlayerModel, ensure_utc_aware, utc_now
from app.domain import rules
from app.schemas.game import (
    CreateRoomRequest,
    EndTurnRequest,
    JoinPlayerRequest,
    RollRequest,
    TileActionRequest,
    UseCardRequest,
)


def _normalize_player_name(name: str) -> str:
    return name.strip()


def _normalize_device_id(device_id: str | None) -> str:
    return (device_id or "").strip()


class GameService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_rooms(self, *, status: str | None = None, limit: int = 30) -> list[dict]:
        self._expire_waiting_rooms()
        stmt = select(RoomModel).order_by(RoomModel.updated_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(RoomModel.status == status)
        rooms = list(self.db.scalars(stmt))
        summaries: list[dict] = []
        for room in rooms:
            self._expire_inactive_players(room)
            players = self._room_players(room.id)
            game = self.db.scalar(select(GameModel).where(GameModel.room_id == room.id))
            summaries.append(self._room_summary(room, players, game))
        return summaries

    def create_room(self, body: CreateRoomRequest) -> dict:
        self._expire_waiting_rooms()
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
        self._expire_waiting_rooms()
        room = self._get_room(room_id)
        if room.status != "waiting":
            raise AppError("房间已经开局，不能加入", 409)

        name = _normalize_player_name(body.name)
        device_id = _normalize_device_id(body.deviceId)
        if not name:
            raise AppError("昵称不能为空", 400)
        if not device_id:
            raise AppError("缺少设备标识", 400)

        existing_players = self._room_players(room_id)
        if self._find_player_by_name(existing_players, name) is not None:
            raise AppError("该房间已有同名玩家，请更换昵称或使用重连", 409)

        bound = self._find_player_by_device(existing_players, device_id)
        if bound is not None and not self._names_equal(bound.name, name):
            raise AppError(
                f"本设备已在该房间使用昵称「{bound.name}」，请用该昵称重连",
                409,
            )

        if len(existing_players) >= room.max_players:
            raise AppError("房间人数已满", 400)

        joined_order = len(existing_players) + 1
        player_id = f"{room_id}_p{joined_order}"
        new_player = RoomPlayerModel(
            id=player_id,
            room_id=room_id,
            name=name,
            avatar_id=body.avatarId,
            piece_color=body.pieceColor,
            saving_goal_type=body.savingGoalType,
            joined_order=joined_order,
            device_id=device_id,
        )
        self._touch_player(new_player)
        self.db.add(new_player)

        game = self._get_game_by_room(room_id)
        room_players = existing_players + [new_player]
        players = self._players_from_room_players(room, room_players)
        game.state_json = rules.sync_waiting_players(game.state_json, players)
        self._touch_room(room)
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return self._mutation_response(game.state_json, None)

    def touch_presence(self, room_id: str, body: JoinPlayerRequest) -> dict:
        self._expire_waiting_rooms()
        room = self._get_room(room_id)
        self._expire_inactive_players(room)

        name = _normalize_player_name(body.name)
        device_id = _normalize_device_id(body.deviceId)
        if not device_id:
            raise AppError("缺少设备标识", 400)

        players = self._room_players(room_id)
        matched = self._find_player_by_device(players, device_id)
        if matched is None:
            matched = self._find_player_by_name(players, name)
        if matched is None:
            raise AppError("你已被移出房间（超过 60 秒未恢复连接）", 404)

        self._touch_player(matched)
        self._touch_room(room)
        self.db.commit()
        return {"ok": True, "playerId": matched.id}

    def rejoin_room(self, room_id: str, body: JoinPlayerRequest) -> dict:
        self._expire_waiting_rooms()
        room = self._get_room(room_id)
        self._expire_inactive_players(room)
        name = _normalize_player_name(body.name)
        device_id = _normalize_device_id(body.deviceId)
        if not name:
            raise AppError("昵称不能为空", 400)
        if not device_id:
            raise AppError("缺少设备标识", 400)

        existing_players = self._room_players(room_id)
        matched = self._find_player_by_name(existing_players, name)
        if matched is None:
            raise AppError("未找到该昵称，可能已被移出房间（超过 60 秒未恢复）", 404)

        bound = self._find_player_by_device(existing_players, device_id)
        if bound is not None and bound.id != matched.id:
            raise AppError(
                f"本设备已绑定昵称「{bound.name}」，请使用该昵称重连",
                409,
            )

        if matched.device_id and matched.device_id != device_id:
            raise AppError("该昵称已在其他设备登录", 403)

        if not matched.device_id:
            matched.device_id = device_id
        self._touch_player(matched)
        self.db.add(matched)

        game = self._get_game_by_room(room_id)
        self._touch_room(room)
        self.db.commit()
        self.db.refresh(game)
        return {
            "gameState": deepcopy(game.state_json),
            "playerId": matched.id,
            "reconnected": True,
        }

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
        self._touch_room(room)
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

    def _expire_waiting_rooms(self) -> None:
        cutoff = utc_now() - timedelta(seconds=WAITING_ROOM_TTL_SECONDS)
        expired_ids = list(
            self.db.scalars(
                select(RoomModel.id).where(
                    RoomModel.status == "waiting",
                    RoomModel.updated_at < cutoff,
                )
            )
        )
        for room_id in expired_ids:
            self._delete_room(room_id)

    def _delete_room(self, room_id: str) -> None:
        self.db.execute(delete(RoomPlayerModel).where(RoomPlayerModel.room_id == room_id))
        self.db.execute(delete(GameModel).where(GameModel.room_id == room_id))
        self.db.execute(delete(RoomModel).where(RoomModel.id == room_id))
        self.db.commit()

    def _touch_room(self, room: RoomModel) -> None:
        room.updated_at = utc_now()
        self.db.add(room)

    def _room_summary(
        self,
        room: RoomModel,
        players: list[RoomPlayerModel],
        game: GameModel | None,
    ) -> dict:
        expires_at = room.updated_at + timedelta(seconds=WAITING_ROOM_TTL_SECONDS)
        return {
            "roomId": room.id,
            "gameId": game.id if game else "",
            "status": room.status,
            "maxPlayers": room.max_players,
            "playerCount": len(players),
            "initialAllowance": room.initial_allowance,
            "playerNames": [p.name for p in players],
            "updatedAt": room.updated_at.isoformat() if room.updated_at else None,
            "expiresAt": expires_at.isoformat() if room.status == "waiting" else None,
            "waitingTtlSeconds": WAITING_ROOM_TTL_SECONDS,
            "playerPresenceTtlSeconds": PLAYER_PRESENCE_TTL_SECONDS,
        }

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
        self._expire_waiting_rooms()
        room = self.db.get(RoomModel, room_id)
        if room is None:
            raise AppError("房间不存在或已超时关闭", 404)
        self._expire_inactive_players(room)
        return room

    def _expire_inactive_players(self, room: RoomModel) -> list[str]:
        if room.status != "waiting":
            return []

        cutoff = utc_now() - timedelta(seconds=PLAYER_PRESENCE_TTL_SECONDS)
        players = self._room_players(room.id)
        kicked_names: list[str] = []
        for player in players:
            last_seen = ensure_utc_aware(player.last_seen_at or player.created_at)
            if last_seen >= cutoff:
                continue
            kicked_names.append(player.name)
            self.db.delete(player)

        if not kicked_names:
            return []

        remaining = self._room_players(room.id)
        game = self._get_game_by_room(room.id)
        game.state_json = rules.sync_waiting_players(
            game.state_json,
            self._players_from_room_players(room, remaining),
        )
        self.db.add(game)
        self._touch_room(room)
        self.db.commit()
        return kicked_names

    @staticmethod
    def _touch_player(player: RoomPlayerModel) -> None:
        player.last_seen_at = utc_now()

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

    @staticmethod
    def _find_player_by_name(
        players: list[RoomPlayerModel], name: str
    ) -> RoomPlayerModel | None:
        key = _normalize_player_name(name).casefold()
        for player in players:
            if _normalize_player_name(player.name).casefold() == key:
                return player
        return None

    @staticmethod
    def _find_player_by_device(
        players: list[RoomPlayerModel], device_id: str
    ) -> RoomPlayerModel | None:
        for player in players:
            if player.device_id == device_id:
                return player
        return None

    @staticmethod
    def _names_equal(a: str, b: str) -> bool:
        return _normalize_player_name(a).casefold() == _normalize_player_name(b).casefold()

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
