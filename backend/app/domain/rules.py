from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from app.core.errors import AppError
from app.domain.seeds import clone_action_cards, clone_board, clone_passive_events


GOAL_RATES = {
    "conservative": 0.20,
    "standard": 0.35,
    "challenge": 0.50,
}

SUPPORTED_CARD_IDS = {
    "card_action_group_buy_discount",
    "card_action_grant",
    "card_action_treat_milk_tea",
    "card_action_overtime_job",
    "card_action_resale",
    "card_action_budget",
}


def clamp(value: int, lower: int = 0, upper: int = 100) -> int:
    return max(lower, min(upper, value))


def create_waiting_state(
    *,
    game_id: str,
    room_id: str,
    max_players: int,
    initial_allowance: int,
) -> dict[str, Any]:
    return {
        "gameId": game_id,
        "roomId": room_id,
        "status": "waiting",
        "round": 1,
        "turnIndex": 0,
        "currentPlayerId": "",
        "initialAllowance": initial_allowance,
        "commonFund": 0,
        "publicReserve": 0,
        "board": clone_board(),
        "players": [],
        "decks": {
            "actionCardDeck": clone_action_cards(),
            "passiveEventDeck": clone_passive_events(),
            "discardPile": [],
        },
        "lastResult": None,
        "settings": {
            "maxPlayers": max_players,
            "maxHandCards": 3,
            "parentTransferInterval": 4,
            "coWinRoundLimit": 20,
        },
        "turnPhase": "waiting",
        "winnerPlayerId": None,
        "creatorPlayerId": "",
        "version": 1,
    }


def make_player(
    *,
    player_id: str,
    name: str,
    avatar_id: str | None,
    piece_color: str | None,
    saving_goal_type: str,
    initial_allowance: int,
) -> dict[str, Any]:
    goal_rate = GOAL_RATES.get(saving_goal_type, GOAL_RATES["standard"])
    return {
        "id": player_id,
        "name": name,
        "avatarId": avatar_id,
        "pieceColor": piece_color,
        "money": initial_allowance,
        "position": 0,
        "bankrupt": False,
        "socialValue": 0,
        "financeValue": 0,
        "mood": 70,
        "energy": 80,
        "grade": 60,
        "cognition": 50,
        "savingGoal": {
            "type": saving_goal_type,
            "targetRate": goal_rate,
            "targetAmount": int(initial_allowance * goal_rate),
            "completed": False,
        },
        "deposits": [],
        "handCards": [],
        "statuses": [],
        "stats": {
            "partTimeCount": 0,
            "studyCount": 0,
            "socialActionCount": 0,
            "helpCount": 0,
            "lowMoodCount": 0,
            "averageEnergyTotal": 0,
            "averageEnergySamples": 0,
        },
        "turnMemory": {
            "lastActionType": "",
            "lastWorkedTurn": -999,
            "consecutiveNoSocialTurns": 0,
            "partTimeBlockedTurns": 0,
        },
        "turnFlags": {
            "rolled": False,
            "usedCard": False,
            "tileActionUsed": False,
        },
    }


def start_game_from_players(
    state: dict[str, Any],
    players: list[dict[str, Any]],
) -> dict[str, Any]:
    new_state = deepcopy(state)
    new_state["players"] = players
    random.shuffle(new_state["decks"]["actionCardDeck"])
    random.shuffle(new_state["decks"]["passiveEventDeck"])
    new_state["status"] = "playing"
    new_state["currentPlayerId"] = players[0]["id"]
    new_state["turnPhase"] = "awaiting_roll"
    new_state["lastResult"] = None
    new_state["version"] = new_state.get("version", 1) + 1
    return new_state


def roll(
    state: dict[str, Any],
    *,
    player_id: str,
    dice: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    new_state = deepcopy(state)
    _require_playing(new_state)
    player = _require_current_player(new_state, player_id)
    if player["turnFlags"].get("rolled"):
        raise AppError("本回合已经掷过骰子", 409)

    dice_value = dice if dice is not None else random.randint(1, 6)
    board = new_state["board"]
    from_position = player["position"]
    to_position = (from_position + dice_value) % len(board)
    tile = board[to_position]
    player["position"] = to_position

    result = _empty_result(player_id, dice_value, from_position, to_position, tile["id"])
    result["messages"].append(f"{player['name']} 掷出 {dice_value}，移动到{tile['name']}")

    if tile.get("cost", 0) > 0:
        cost = _apply_personal_discount(player, int(tile["cost"]))
        _change_player(player, result, money=-cost)
        result["messages"].append(f"{tile['name']}消费 {cost} 元")

    event = _draw_passive_event(new_state)
    if event is not None:
        result["triggeredEventId"] = event["id"]
        _apply_passive_event(player, event, result)

    card = _draw_action_card(new_state, player)
    if card is not None:
        result["drawnCardId"] = card["id"]
        result["messages"].append(f"抽到行动牌：{card['name']}")

    player["turnFlags"]["rolled"] = True
    new_state["turnPhase"] = "awaiting_action"
    _finish_mutation(new_state, result)
    return new_state, result


def tile_action(
    state: dict[str, Any],
    *,
    player_id: str,
    action: str,
    target_player_id: str | None = None,
    amount: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    new_state = deepcopy(state)
    _require_playing(new_state)
    player = _require_current_player(new_state, player_id)
    if not player["turnFlags"].get("rolled"):
        raise AppError("请先掷骰再执行地块行动", 409)
    if player["turnFlags"].get("tileActionUsed"):
        raise AppError("本回合已经执行过地块行动", 409)

    tile = _current_tile(new_state, player)
    if action not in tile.get("actions", []):
        raise AppError(f"{tile['name']} 不支持动作 {action}", 400)

    result = _empty_result(player_id, 0, player["position"], player["position"], tile["id"])

    if action == "part_time":
        _do_part_time(new_state, player, result)
    elif action == "study":
        _do_study(player, result)
    elif action == "rest":
        _change_player(player, result, mood=15, energy=25)
        result["messages"].append("在宿舍休息，恢复心情和精力")
    elif action == "social_interaction":
        _do_social_interaction(new_state, player, target_player_id, result)
    elif action == "deposit":
        _do_deposit(player, amount, result)
    else:
        raise AppError(f"动作 {action} 暂未实现", 400)

    player["turnFlags"]["tileActionUsed"] = True
    _finish_mutation(new_state, result)
    return new_state, result


def use_card(
    state: dict[str, Any],
    *,
    player_id: str,
    card_id: str,
    target_player_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    new_state = deepcopy(state)
    _require_playing(new_state)
    player = _require_current_player(new_state, player_id)
    if player["turnFlags"].get("usedCard"):
        raise AppError("本回合已经使用过行动牌", 409)

    card = _remove_card_from_hand(player, card_id)
    if card["id"] not in SUPPORTED_CARD_IDS:
        player["handCards"].append(card)
        raise AppError(f"行动牌「{card['name']}」需要多人交互，首期暂未实现", 400)

    result = _empty_result(player_id, 0, player["position"], player["position"], _current_tile(new_state, player)["id"])

    if card_id == "card_action_grant":
        bonus = 350 if _is_lowest_money(new_state, player) else 300
        _change_player(player, result, money=bonus)
        result["messages"].append(f"使用「申请助学金」，获得 {bonus} 元")
    elif card_id == "card_action_overtime_job":
        if player["turnMemory"].get("lastActionType") == "part_time":
            player["handCards"].append(card)
            raise AppError("上一回合已经兼职，不能使用兼职加班", 400)
        _change_player(player, result, money=400, energy=-35, mood=-5)
        player["turnMemory"]["lastActionType"] = "part_time"
        player["stats"]["partTimeCount"] += 1
        result["messages"].append("使用「兼职加班」，获得 400 元")
    elif card_id == "card_action_resale":
        _change_player(player, result, money=250)
        result["messages"].append("使用「闲置物品转卖」，获得 250 元")
    elif card_id == "card_action_budget":
        _add_status(player, "status_budget", "预算", 2, "card_action_budget", {"expenseRate": 0.5})
        _change_player(player, result, cognition=5)
        result["messages"].append("使用「制定预算」，接下来 2 回合个人消费减半")
    elif card_id == "card_action_group_buy_discount":
        _add_status(
            player,
            "status_group_buy_discount",
            "拼单省钱",
            1,
            "card_action_group_buy_discount",
            {"expenseRate": 0.5},
        )
        result["messages"].append("使用「拼单省钱」，下回合个人消费减半")
    elif card_id == "card_action_treat_milk_tea":
        _change_player(player, result, money=-200, social=1)
        for other in _other_active_players(new_state, player_id):
            other["money"] += 50
        result["messages"].append("使用「请客喝奶茶」，自己扣除 200 元，其他玩家各获得 50 元")

    player["turnFlags"]["usedCard"] = True
    new_state["decks"]["discardPile"].append(card)
    _finish_mutation(new_state, result)
    return new_state, result


def end_turn(
    state: dict[str, Any],
    *,
    player_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    new_state = deepcopy(state)
    _require_playing(new_state)
    player = _require_current_player(new_state, player_id)
    result = _empty_result(player_id, 0, player["position"], player["position"], _current_tile(new_state, player)["id"])

    _tick_statuses(player)
    if player["turnMemory"].get("partTimeBlockedTurns", 0) > 0:
        player["turnMemory"]["partTimeBlockedTurns"] -= 1

    player["stats"]["averageEnergyTotal"] += player["energy"]
    player["stats"]["averageEnergySamples"] += 1
    player["bankrupt"] = player["money"] < 0
    if player["bankrupt"]:
        result["messages"].append(f"{player['name']} 资金为负，进入破产状态")

    active = [p for p in new_state["players"] if not p["bankrupt"]]
    if len(active) <= 1 and active:
        new_state["status"] = "finished"
        new_state["winnerPlayerId"] = active[0]["id"]
        new_state["currentPlayerId"] = active[0]["id"]
        new_state["turnPhase"] = "finished"
        result["messages"].append(f"游戏结束，{active[0]['name']} 获胜")
    else:
        _advance_turn(new_state)
        result["messages"].append(f"回合结束，轮到 {_current_player(new_state)['name']}")

    _finish_mutation(new_state, result)
    return new_state, result


def sync_waiting_players(state: dict[str, Any], players: list[dict[str, Any]]) -> dict[str, Any]:
    new_state = deepcopy(state)
    new_state["players"] = players
    new_state["version"] = new_state.get("version", 1) + 1
    return new_state


def _require_playing(state: dict[str, Any]) -> None:
    if state["status"] != "playing":
        raise AppError("游戏当前不在 playing 状态", 409)


def _require_current_player(state: dict[str, Any], player_id: str) -> dict[str, Any]:
    if state["currentPlayerId"] != player_id:
        raise AppError("当前不是该玩家的回合", 409)
    return _find_player(state, player_id)


def _find_player(state: dict[str, Any], player_id: str) -> dict[str, Any]:
    for player in state["players"]:
        if player["id"] == player_id:
            return player
    raise AppError("玩家不存在", 404)


def _current_player(state: dict[str, Any]) -> dict[str, Any]:
    return _find_player(state, state["currentPlayerId"])


def _current_tile(state: dict[str, Any], player: dict[str, Any]) -> dict[str, Any]:
    return state["board"][player["position"]]


def _empty_result(
    player_id: str,
    dice: int,
    from_position: int,
    to_position: int,
    tile_id: str,
) -> dict[str, Any]:
    return {
        "playerId": player_id,
        "dice": dice,
        "fromPosition": from_position,
        "toPosition": to_position,
        "tileId": tile_id,
        "moneyDelta": 0,
        "moodDelta": 0,
        "energyDelta": 0,
        "gradeDelta": 0,
        "cognitionDelta": 0,
        "socialValueDelta": 0,
        "financeValueDelta": 0,
        "messages": [],
    }


def _change_player(
    player: dict[str, Any],
    result: dict[str, Any],
    *,
    money: int = 0,
    mood: int = 0,
    energy: int = 0,
    grade: int = 0,
    cognition: int = 0,
    social: int = 0,
    finance: int = 0,
) -> None:
    player["money"] += money
    player["mood"] = clamp(player["mood"] + mood)
    player["energy"] = clamp(player["energy"] + energy)
    player["grade"] = clamp(player["grade"] + grade)
    player["cognition"] = clamp(player["cognition"] + cognition)
    player["socialValue"] += social
    player["financeValue"] += finance
    result["moneyDelta"] += money
    result["moodDelta"] += mood
    result["energyDelta"] += energy
    result["gradeDelta"] += grade
    result["cognitionDelta"] += cognition
    result["socialValueDelta"] += social
    result["financeValueDelta"] += finance


def _draw_action_card(state: dict[str, Any], player: dict[str, Any]) -> dict[str, Any] | None:
    deck = state["decks"]["actionCardDeck"]
    if not deck:
        discard = state["decks"]["discardPile"]
        state["decks"]["actionCardDeck"] = discard
        state["decks"]["discardPile"] = []
        random.shuffle(state["decks"]["actionCardDeck"])
        deck = state["decks"]["actionCardDeck"]
    if not deck:
        return None
    card = deck.pop(0)
    player["handCards"].append(card)
    max_cards = state["settings"]["maxHandCards"]
    if len(player["handCards"]) > max_cards:
        discarded = player["handCards"].pop(0)
        state["decks"]["discardPile"].append(discarded)
    return card


def _draw_passive_event(state: dict[str, Any]) -> dict[str, Any] | None:
    deck = state["decks"]["passiveEventDeck"]
    if not deck:
        state["decks"]["passiveEventDeck"] = clone_passive_events()
        random.shuffle(state["decks"]["passiveEventDeck"])
        deck = state["decks"]["passiveEventDeck"]
    return deck.pop(0) if deck else None


def _apply_passive_event(player: dict[str, Any], event: dict[str, Any], result: dict[str, Any]) -> None:
    if "moneyRange" in event:
        money = random.randint(event["moneyRange"][0], event["moneyRange"][1])
        _change_player(player, result, money=money)
        result["messages"].append(f"被动事件「{event['name']}」：获得 {money} 元")
        return
    if any(key in event for key in ("money", "mood", "energy", "grade", "cognition")):
        _change_player(
            player,
            result,
            money=int(event.get("money", 0)),
            mood=int(event.get("mood", 0)),
            energy=int(event.get("energy", 0)),
            grade=int(event.get("grade", 0)),
            cognition=int(event.get("cognition", 0)),
        )
        if "partTimeBlockedTurns" in event:
            player["turnMemory"]["partTimeBlockedTurns"] = int(event["partTimeBlockedTurns"])
        result["messages"].append(f"被动事件「{event['name']}」已结算")
        return
    result["messages"].append(f"被动事件「{event['name']}」需要后续交互，首期仅记录")


def _apply_personal_discount(player: dict[str, Any], cost: int) -> int:
    discount_rate = 1.0
    for status in player["statuses"]:
        effect = status.get("effect") or {}
        if "expenseRate" in effect:
            discount_rate = min(discount_rate, float(effect["expenseRate"]))
    return int(cost * discount_rate)


def _do_part_time(state: dict[str, Any], player: dict[str, Any], result: dict[str, Any]) -> None:
    if player["energy"] < 30:
        raise AppError("精力低于 30，不能兼职", 400)
    if player["turnMemory"].get("partTimeBlockedTurns", 0) > 0:
        raise AppError("补考状态期间不能兼职", 400)
    if player["turnMemory"].get("lastActionType") == "part_time":
        raise AppError("不能连续两个自己的回合都兼职", 400)
    income = random.randint(100, 300)
    _change_player(player, result, money=income, energy=-30, mood=-5, cognition=3)
    player["turnMemory"]["lastActionType"] = "part_time"
    player["turnMemory"]["lastWorkedTurn"] = state["turnIndex"]
    player["stats"]["partTimeCount"] += 1
    result["messages"].append(f"执行兼职，获得 {income} 元")


def _do_study(player: dict[str, Any], result: dict[str, Any]) -> None:
    if player["energy"] < 30:
        raise AppError("精力低于 30，不能学习", 400)
    _change_player(player, result, mood=-5, energy=-20, grade=8, cognition=5)
    player["turnMemory"]["lastActionType"] = "study"
    player["stats"]["studyCount"] += 1
    result["messages"].append("在图书馆学习，成绩 +8，认知 +5")


def _do_social_interaction(
    state: dict[str, Any],
    player: dict[str, Any],
    target_player_id: str | None,
    result: dict[str, Any],
) -> None:
    if not target_player_id:
        raise AppError("社交互动需要 targetPlayerId", 400)
    target = _find_player(state, target_player_id)
    if target["id"] == player["id"]:
        raise AppError("不能和自己进行社交互动", 400)
    _change_player(player, result, mood=10, energy=-10, social=1)
    target["mood"] = clamp(target["mood"] + 10)
    target["energy"] = clamp(target["energy"] - 10)
    target["socialValue"] += 1
    player["stats"]["socialActionCount"] += 1
    result["messages"].append(f"与 {target['name']} 社交互动，双方社交值 +1")


def _do_deposit(player: dict[str, Any], amount: int | None, result: dict[str, Any]) -> None:
    deposit_amount = amount or min(200, max(0, player["money"]))
    if deposit_amount <= 0 or player["money"] < deposit_amount:
        raise AppError("存款金额不合法", 400)
    player["money"] -= deposit_amount
    player["deposits"].append({"amount": deposit_amount, "turnsLeft": 3, "rate": 0.12 if player["cognition"] >= 70 else 0.10})
    result["moneyDelta"] -= deposit_amount
    result["messages"].append(f"办理定期存款 {deposit_amount} 元")


def _remove_card_from_hand(player: dict[str, Any], card_id: str) -> dict[str, Any]:
    for index, card in enumerate(player["handCards"]):
        if card["id"] == card_id:
            return player["handCards"].pop(index)
    raise AppError("手牌中没有这张行动牌", 400)


def _is_lowest_money(state: dict[str, Any], player: dict[str, Any]) -> bool:
    active_money = [p["money"] for p in state["players"] if not p["bankrupt"]]
    return bool(active_money) and player["money"] == min(active_money)


def _add_status(
    player: dict[str, Any],
    status_id: str,
    name: str,
    duration: int | None,
    source: str,
    effect: dict[str, Any],
) -> None:
    player["statuses"] = [s for s in player["statuses"] if s["id"] != status_id]
    player["statuses"].append(
        {"id": status_id, "name": name, "duration": duration, "source": source, "effect": effect}
    )


def _other_active_players(state: dict[str, Any], player_id: str) -> list[dict[str, Any]]:
    return [p for p in state["players"] if p["id"] != player_id and not p["bankrupt"]]


def _tick_statuses(player: dict[str, Any]) -> None:
    kept = []
    for status in player["statuses"]:
        duration = status.get("duration")
        if duration is None:
            kept.append(status)
            continue
        next_duration = duration - 1
        if next_duration > 0:
            status["duration"] = next_duration
            kept.append(status)
    player["statuses"] = kept


def _advance_turn(state: dict[str, Any]) -> None:
    players = state["players"]
    current_index = next(
        index for index, player in enumerate(players) if player["id"] == state["currentPlayerId"]
    )
    next_index = current_index
    for _ in range(len(players)):
        next_index = (next_index + 1) % len(players)
        if not players[next_index]["bankrupt"]:
            break
    if next_index <= current_index:
        state["round"] += 1
    state["turnIndex"] += 1
    state["currentPlayerId"] = players[next_index]["id"]
    players[next_index]["turnFlags"] = {"rolled": False, "usedCard": False, "tileActionUsed": False}
    state["turnPhase"] = "awaiting_roll"


def _finish_mutation(state: dict[str, Any], result: dict[str, Any]) -> None:
    state["lastResult"] = result
    state["version"] = state.get("version", 1) + 1
    for player in state["players"]:
        if player["mood"] < 30:
            _add_status(
                player,
                "status_low_mood",
                "低落",
                None,
                "mood_below_30",
                {"cannotStartGroupParty": True, "extraExpenseOnConsumptionEvent": 50},
            )
        player["bankrupt"] = player["money"] < 0
