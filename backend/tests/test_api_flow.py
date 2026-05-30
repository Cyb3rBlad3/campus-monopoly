from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db.session import configure_engine, init_db
from app.main import app

TEST_DEVICE = "dev_test_client_01"
TEST_DEVICE_B = "dev_test_client_02"


@pytest.fixture()
def client(tmp_path: Path):
    configure_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    init_db()
    with TestClient(app) as test_client:
        yield test_client


def create_started_game(client: TestClient) -> dict:
    room_res = client.post("/api/rooms", json={"maxPlayers": 4, "initialAllowance": 2000})
    assert room_res.status_code == 200
    room_state = room_res.json()
    room_id = room_state["roomId"]

    for name in ["阿明", "小夏"]:
        join_res = client.post(
            f"/api/rooms/{room_id}/players",
            json={"name": name, "deviceId": f"{TEST_DEVICE}_{name}"},
        )
        assert join_res.status_code == 200

    start_res = client.post(
        f"/api/rooms/{room_id}/start",
        json={"playerId": f"{room_id}_p1", "deviceId": f"{TEST_DEVICE}_阿明"},
    )
    assert start_res.status_code == 200
    return start_res.json()["gameState"]


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_room_join_start_and_get_game(client: TestClient):
    state = create_started_game(client)
    assert state["status"] == "playing"
    assert len(state["players"]) == 2
    assert state["currentPlayerId"] == state["players"][0]["id"]

    get_res = client.get(f"/api/games/{state['gameId']}")
    assert get_res.status_code == 200
    loaded = get_res.json()
    assert loaded["gameId"] == state["gameId"]
    assert loaded["board"][9]["actions"] == ["part_time"]


def test_cannot_start_with_one_player(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    join_res = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "单人玩家", "deviceId": TEST_DEVICE},
    )
    assert join_res.status_code == 200

    start_res = client.post(
        f"/api/rooms/{room_id}/start",
        json={"playerId": f"{room_id}_p1", "deviceId": TEST_DEVICE},
    )
    assert start_res.status_code == 400
    assert "至少需要 2 名玩家" in start_res.json()["message"]


def test_only_room_creator_can_start(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    for name in ["房主", "路人"]:
        join_res = client.post(
            f"/api/rooms/{room_id}/players",
            json={"name": name, "deviceId": f"{TEST_DEVICE}_{name}"},
        )
        assert join_res.status_code == 200

    denied = client.post(
        f"/api/rooms/{room_id}/start",
        json={"playerId": f"{room_id}_p2", "deviceId": f"{TEST_DEVICE}_路人"},
    )
    assert denied.status_code == 403
    assert "只有创建房间的玩家可以开始游戏" in denied.json()["message"]

    allowed = client.post(
        f"/api/rooms/{room_id}/start",
        json={"playerId": f"{room_id}_p1", "deviceId": f"{TEST_DEVICE}_房主"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["gameState"]["status"] == "playing"


def test_first_joiner_is_room_creator(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    join_res = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "房主", "deviceId": TEST_DEVICE},
    )
    assert join_res.status_code == 200
    state = join_res.json()["gameState"]
    assert state["creatorPlayerId"] == f"{room_id}_p1"


def test_roll_updates_position_hand_and_last_result(client: TestClient):
    state = create_started_game(client)
    game_id = state["gameId"]
    player_id = state["currentPlayerId"]

    roll_res = client.post(f"/api/games/{game_id}/roll", json={"playerId": player_id, "dice": 3})
    assert roll_res.status_code == 200
    payload = roll_res.json()
    next_state = payload["gameState"]
    result = payload["turnResult"]

    player = next(p for p in next_state["players"] if p["id"] == player_id)
    assert player["position"] == 3
    assert len(player["handCards"]) == 1
    assert result["dice"] == 3
    assert result["toPosition"] == 3
    assert next_state["lastResult"]["playerId"] == player_id


def test_non_current_player_cannot_roll(client: TestClient):
    state = create_started_game(client)
    game_id = state["gameId"]
    other_player_id = state["players"][1]["id"]

    roll_res = client.post(f"/api/games/{game_id}/roll", json={"playerId": other_player_id, "dice": 2})
    assert roll_res.status_code == 409
    assert "当前不是该玩家" in roll_res.json()["message"]


def test_tile_action_study_updates_growth_values(client: TestClient):
    state = create_started_game(client)
    game_id = state["gameId"]
    player_id = state["currentPlayerId"]

    roll_res = client.post(f"/api/games/{game_id}/roll", json={"playerId": player_id, "dice": 2})
    assert roll_res.status_code == 200

    action_res = client.post(
        f"/api/games/{game_id}/tile-action",
        json={"playerId": player_id, "action": "study"},
    )
    assert action_res.status_code == 200
    payload = action_res.json()
    acted = payload["gameState"]
    acted_player = next(p for p in acted["players"] if p["id"] == player_id)
    assert acted_player["turnMemory"]["lastActionType"] == "study"
    assert payload["turnResult"]["gradeDelta"] == 8
    assert payload["turnResult"]["cognitionDelta"] == 5


def test_duplicate_name_rejected_on_join(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    assert (
        client.post(
            f"/api/rooms/{room_id}/players",
            json={"name": "阿明", "deviceId": TEST_DEVICE},
        ).status_code
        == 200
    )
    dup = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "阿明", "deviceId": TEST_DEVICE_B},
    )
    assert dup.status_code == 409
    assert "同名" in dup.json()["message"]


def test_same_device_cannot_use_second_name(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    assert (
        client.post(
            f"/api/rooms/{room_id}/players",
            json={"name": "阿明", "deviceId": TEST_DEVICE},
        ).status_code
        == 200
    )
    second = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "小夏", "deviceId": TEST_DEVICE},
    )
    assert second.status_code == 409
    assert "本设备" in second.json()["message"]


def test_rejoin_restores_player_id(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    join_res = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "小夏", "deviceId": TEST_DEVICE},
    )
    player_id = join_res.json()["gameState"]["players"][0]["id"]

    rejoin_res = client.post(
        f"/api/rooms/{room_id}/rejoin",
        json={"name": "小夏", "deviceId": TEST_DEVICE},
    )
    assert rejoin_res.status_code == 200
    payload = rejoin_res.json()
    assert payload["playerId"] == player_id
    assert payload["reconnected"] is True


def test_inactive_player_kicked_from_waiting_room(client: TestClient):
    from datetime import timedelta

    from app.db.models import RoomPlayerModel, utc_now
    from app.db.session import SessionLocal

    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    join_res = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "挂机玩家", "deviceId": TEST_DEVICE},
    )
    assert join_res.status_code == 200
    player_id = join_res.json()["gameState"]["players"][0]["id"]

    db = SessionLocal()
    try:
        player = db.get(RoomPlayerModel, player_id)
        assert player is not None
        player.last_seen_at = utc_now() - timedelta(seconds=61)
        db.add(player)
        db.commit()
    finally:
        db.close()

    listed = client.get("/api/rooms", params={"status": "waiting"})
    row = next(r for r in listed.json() if r["roomId"] == room_id)
    assert row["playerCount"] == 0

    gone = client.post(
        f"/api/rooms/{room_id}/rejoin",
        json={"name": "挂机玩家", "deviceId": TEST_DEVICE},
    )
    assert gone.status_code == 404


def test_presence_keeps_player_in_room(client: TestClient):
    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]
    client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "在线", "deviceId": TEST_DEVICE},
    )
    ping = client.post(
        f"/api/rooms/{room_id}/presence",
        json={"name": "在线", "deviceId": TEST_DEVICE},
    )
    assert ping.status_code == 200
    assert ping.json()["playerId"].endswith("_p1")


def test_waiting_room_expires_after_ttl(client: TestClient):
    from datetime import timedelta

    from app.core.room_policy import WAITING_ROOM_TTL_SECONDS
    from app.db.models import RoomModel, utc_now
    from app.db.session import SessionLocal

    room_res = client.post("/api/rooms", json={})
    room_id = room_res.json()["roomId"]

    db = SessionLocal()
    try:
        room = db.get(RoomModel, room_id)
        assert room is not None
        room.updated_at = utc_now() - timedelta(seconds=WAITING_ROOM_TTL_SECONDS + 1)
        db.add(room)
        db.commit()
    finally:
        db.close()

    listed = client.get("/api/rooms")
    assert all(row["roomId"] != room_id for row in listed.json())

    missing = client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "玩家", "deviceId": TEST_DEVICE},
    )
    assert missing.status_code == 404


def test_list_rooms_includes_waiting_room(client: TestClient):
    room_res = client.post("/api/rooms", json={"initialAllowance": 1500})
    room_id = room_res.json()["roomId"]
    client.post(
        f"/api/rooms/{room_id}/players",
        json={"name": "玩家A", "deviceId": TEST_DEVICE},
    )

    listed = client.get("/api/rooms", params={"status": "waiting"})
    assert listed.status_code == 200
    rows = listed.json()
    assert any(row["roomId"] == room_id and row["playerCount"] == 1 for row in rows)


def test_end_turn_switches_current_player(client: TestClient):
    state = create_started_game(client)
    game_id = state["gameId"]
    first_player = state["currentPlayerId"]
    second_player = state["players"][1]["id"]

    roll_res = client.post(f"/api/games/{game_id}/roll", json={"playerId": first_player, "dice": 1})
    assert roll_res.status_code == 200
    end_res = client.post(f"/api/games/{game_id}/end-turn", json={"playerId": first_player})
    assert end_res.status_code == 200
    assert end_res.json()["gameState"]["currentPlayerId"] == second_player


def test_roll_sets_turn_deadline_and_context(client: TestClient):
    state = create_started_game(client)
    game_id = state["gameId"]
    player_id = state["currentPlayerId"]

    roll_res = client.post(f"/api/games/{game_id}/roll", json={"playerId": player_id, "dice": 2})
    assert roll_res.status_code == 200
    next_state = roll_res.json()["gameState"]
    result = roll_res.json()["turnResult"]

    assert next_state["turnPhase"] == "awaiting_action"
    assert next_state["turnDeadlineAt"]
    assert next_state["currentTurnContext"]["playerId"] == player_id
    assert next_state["currentTurnContext"]["triggeredEventId"] == result.get("triggeredEventId")
    assert next_state["currentTurnContext"]["drawnCardId"] == result.get("drawnCardId")
    assert next_state["settings"]["turnActionLimitSeconds"] == 35


def test_end_turn_clears_turn_timing(client: TestClient):
    state = create_started_game(client)
    game_id = state["gameId"]
    player_id = state["currentPlayerId"]

    client.post(f"/api/games/{game_id}/roll", json={"playerId": player_id, "dice": 1})
    end_res = client.post(f"/api/games/{game_id}/end-turn", json={"playerId": player_id})
    assert end_res.status_code == 200
    next_state = end_res.json()["gameState"]
    assert next_state["turnDeadlineAt"] is None
    assert next_state["currentTurnContext"] is None
    assert next_state["turnPhase"] == "awaiting_roll"


def test_expired_deadline_auto_ends_turn_on_get_game(client: TestClient):
    from datetime import timedelta

    from app.db.models import utc_now
    from app.db.session import SessionLocal
    from app.db.models import GameModel

    state = create_started_game(client)
    game_id = state["gameId"]
    first_player = state["currentPlayerId"]
    second_player = state["players"][1]["id"]

    roll_res = client.post(f"/api/games/{game_id}/roll", json={"playerId": first_player, "dice": 1})
    assert roll_res.status_code == 200

    with SessionLocal() as db:
        game = db.get(GameModel, game_id)
        assert game is not None
        game.state_json["turnDeadlineAt"] = (utc_now() - timedelta(seconds=1)).isoformat()
        db.add(game)
        db.commit()

    get_res = client.get(f"/api/games/{game_id}")
    assert get_res.status_code == 200
    loaded = get_res.json()
    assert loaded["currentPlayerId"] == second_player
    assert loaded["turnDeadlineAt"] is None
    assert loaded["currentTurnContext"] is None
    assert any("行动超时" in msg for msg in loaded["lastResult"]["messages"])
