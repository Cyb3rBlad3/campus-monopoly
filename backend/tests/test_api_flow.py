from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db.session import configure_engine, init_db
from app.main import app


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
        join_res = client.post(f"/api/rooms/{room_id}/players", json={"name": name})
        assert join_res.status_code == 200

    start_res = client.post(f"/api/rooms/{room_id}/start", json={})
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
    join_res = client.post(f"/api/rooms/{room_id}/players", json={"name": "单人玩家"})
    assert join_res.status_code == 200

    start_res = client.post(f"/api/rooms/{room_id}/start", json={})
    assert start_res.status_code == 400
    assert "至少需要 2 名玩家" in start_res.json()["message"]


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
