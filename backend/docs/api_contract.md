# 后端 API 契约

本文档以 `front_end/src/api/game.ts`、`front_end/src/api/http.ts` 和 `CampusMonopoly_Improved_Rules.md` 第十三节为依据。

## 通用约定

- API 根路径由前端 `VITE_API_BASE_URL` 决定，后端只暴露 `/api/...`。
- JSON 写接口接收 `application/json`。
- 读取接口 `GET /api/games/:gameId` 直接返回完整 `GameState`。
- 写接口返回 `{ "gameState": GameState, "turnResult": TurnResult | null }`。
- 错误响应统一为 `{ "message": "错误说明" }`。

## POST /api/rooms

用途：创建宿舍房间。

请求体：

```json
{
  "maxPlayers": 4,
  "initialAllowance": 2000
}
```

响应：完整 `GameState`。首期状态为 `waiting`，玩家列表为空。

## POST /api/rooms/:roomId/players

用途：加入玩家。

请求体：

```json
{
  "name": "玩家1",
  "avatarId": "avatar_01",
  "pieceColor": "#38b987",
  "savingGoalType": "standard"
}
```

响应：

```json
{
  "gameState": {},
  "turnResult": null
}
```

## POST /api/rooms/:roomId/start

用途：初始化对局并开局。

请求体：`{}`。

响应：`{ "gameState": GameState, "turnResult": null }`。

## GET /api/games/:gameId

用途：获取完整 `GameState`。

响应：完整 `GameState`。

## POST /api/games/:gameId/roll

用途：当前玩家投骰、移动、结算基础地块、触发被动事件并抽牌。

请求体：

```json
{
  "playerId": "p1",
  "dice": 4
}
```

`dice` 仅用于测试和可复现联调；正常请求可以省略。

响应：`{ "gameState": GameState, "turnResult": TurnResult }`。

## POST /api/games/:gameId/tile-action

用途：执行当前地块允许的主动行动。

请求体：

```json
{
  "playerId": "p1",
  "action": "part_time",
  "targetPlayerId": "p2",
  "amount": 200
}
```

首期支持动作：`part_time`、`study`、`rest`、`social_interaction`、`deposit`。

响应：`{ "gameState": GameState, "turnResult": TurnResult }`。

## POST /api/games/:gameId/use-card

用途：使用行动牌。

请求体：

```json
{
  "playerId": "p1",
  "cardId": "card_action_budget",
  "targetPlayerId": "p2"
}
```

响应：`{ "gameState": GameState, "turnResult": TurnResult }`。

## POST /api/games/:gameId/end-turn

用途：结束当前玩家回合，结算状态并切换玩家。

请求体：

```json
{
  "playerId": "p1"
}
```

响应：`{ "gameState": GameState, "turnResult": TurnResult }`。

## 状态码

- `400`：请求参数错误或规则不允许。
- `404`：房间或游戏不存在。
- `409`：游戏状态冲突，例如未开局掷骰、不是当前玩家、重复掷骰。
