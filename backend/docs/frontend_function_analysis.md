# 前端函数解读

本文档记录 `front_end` 已经写出的函数、页面方法和类型契约。写法固定为：做什么、输入、输出、暗示后端需要什么能力。

## src/api/game.ts

### createRoom(body?)

- 做什么：调用 `POST /api/rooms` 创建宿舍房间。
- 输入：可选的普通对象，当前前端没有固定字段。
- 输出：`ApiResult<GameState | { roomId: string }>`。
- 后端能力：需要提供创建房间接口。为了后续接口统一，后端首期直接返回完整 `GameState`。

### joinRoom(roomId, body?)

- 做什么：调用 `POST /api/rooms/:roomId/players` 加入玩家。
- 输入：`roomId` 路径参数和可选玩家信息对象。
- 输出：`ApiResult<{ gameState, turnResult? }>`。
- 后端能力：需要检查房间是否存在、是否可加入、人数是否超过上限，并返回更新后的完整状态。

### startRoom(roomId, body?)

- 做什么：调用 `POST /api/rooms/:roomId/start` 开局。
- 输入：`roomId` 路径参数和可选开局参数。
- 输出：`ApiResult<{ gameState, turnResult? }>`。
- 后端能力：需要从房间玩家初始化棋盘、玩家数值、牌堆和当前回合。

### getGame(gameId)

- 做什么：调用 `GET /api/games/:gameId` 获取完整 `GameState`。
- 输入：`gameId` 路径参数。
- 输出：`ApiResult<GameState>`。
- 后端能力：需要能按 `gameId` 读取完整游戏快照，字段必须兼容前端 `GameState`。

### rollDice(gameId, body?)

- 做什么：调用 `POST /api/games/:gameId/roll` 执行掷骰和移动。
- 输入：`gameId` 路径参数和可选操作对象。
- 输出：`ApiResult<{ gameState, turnResult? }>`。
- 后端能力：需要校验当前玩家，完成掷骰、移动、基础地块结算、被动事件和抽牌。

### tileAction(gameId, body?)

- 做什么：调用 `POST /api/games/:gameId/tile-action` 执行地块主动行动。
- 输入：`gameId` 路径参数和可选操作对象。
- 输出：`ApiResult<{ gameState, turnResult? }>`。
- 后端能力：需要根据当前地块允许动作执行兼职、学习、休息、社交、储蓄等规则。

### useCard(gameId, body?)

- 做什么：调用 `POST /api/games/:gameId/use-card` 使用行动牌。
- 输入：`gameId` 路径参数和可选操作对象。
- 输出：`ApiResult<{ gameState, turnResult? }>`。
- 后端能力：需要校验手牌、目标玩家和每回合用牌限制，并执行已支持的卡牌效果。

### endTurn(gameId, body?)

- 做什么：调用 `POST /api/games/:gameId/end-turn` 结束当前玩家回合。
- 输入：`gameId` 路径参数和可选操作对象。
- 输出：`ApiResult<{ gameState, turnResult? }>`。
- 后端能力：需要结算回合末状态、破产、胜利，并切换到下一名可行动玩家。

## src/api/http.ts

### joinUrl(path)

- 做什么：把 API 根地址和接口路径拼接起来，并保证路径以 `/` 开头。
- 输入：接口路径字符串。
- 输出：最终请求 URL。
- 后端能力：后端只需要暴露 `/api/...` 路由；前端通过 `VITE_API_BASE_URL` 决定真实域名。

### apiRequest(options)

- 做什么：封装 `uni.request`，把 HTTP 结果转成统一的 `ApiResult<T>`。
- 输入：uni-app 请求配置，必须包含 `url`。
- 输出：成功时 `{ ok: true, data }`，失败时 `{ ok: false, statusCode, message }`。
- 后端能力：错误响应体应该包含 `message` 字段，否则前端只能显示 `HTTP 状态码`。

### postJson(path, body?)

- 做什么：发送 JSON POST 请求。
- 输入：接口路径和可选 JSON 请求体。
- 输出：`ApiResult<T>`。
- 后端能力：所有写操作接口应接收 `application/json`。

### getJson(path)

- 做什么：发送 GET 请求。
- 输入：接口路径。
- 输出：`ApiResult<T>`。
- 后端能力：状态读取接口应能直接返回 JSON。

## src/config/env.ts

### getApiBaseUrl()

- 做什么：读取 `VITE_API_BASE_URL`，并去掉末尾斜杠。
- 输入：构建环境变量。
- 输出：API 根地址字符串，未配置时为空字符串。
- 后端能力：本地开发默认运行在 `http://127.0.0.1:8000`，前端可配置该地址联调。

## src/stores/session.ts

### useSessionStore()

- 做什么：定义本地会话 store。
- 输入：无。
- 输出：`roomId`、`gameId`、`localPlayerId` 和对应 setter。
- 后端能力：接口和响应需要稳定提供 `roomId`、`gameId`、`playerId`，让前端能保存并再次请求。

### setRoom(id)

- 做什么：保存当前房间 ID。
- 输入：房间 ID。
- 输出：更新 Pinia 状态。
- 后端能力：创建房间和加入玩家流程必须返回可展示和复用的 `roomId`。

### setGame(id)

- 做什么：保存当前对局 ID。
- 输入：对局 ID。
- 输出：更新 Pinia 状态。
- 后端能力：开局或创建房间后必须能得到 `gameId`，用于 `GET /api/games/:gameId`。

### setLocalPlayer(id)

- 做什么：保存本机玩家 ID。
- 输入：玩家 ID。
- 输出：更新 Pinia 状态。
- 后端能力：加入玩家时应返回包含玩家 ID 的 `GameState.players`。

### clear()

- 做什么：清空本地会话字段。
- 输入：无。
- 输出：清空 Pinia 状态。
- 后端能力：无直接要求。

## src/stores/game.ts

### useGameStore()

- 做什么：定义对局状态 store。
- 输入：无。
- 输出：当前 `GameState`、最近 `TurnResult`、loading、错误消息、当前玩家计算属性。
- 后端能力：写操作应返回完整 `GameState` 和可选 `TurnResult`，读取操作应直接返回完整 `GameState`。

### currentPlayer

- 做什么：根据 `gameState.currentPlayerId` 在 `players` 中查找当前玩家。
- 输入：当前 `GameState`。
- 输出：当前玩家对象或 `null`。
- 后端能力：`currentPlayerId` 必须始终指向 `players` 中存在且可行动的玩家，游戏结束时也要保持可解释。

### setFromResponse(gs, turn?)

- 做什么：把后端响应写入 store，并选择最近一次回合结果。
- 输入：完整 `GameState` 和可选 `TurnResult`。
- 输出：更新 `gameState` 与 `lastTurnResult`。
- 后端能力：写操作优先返回 `turnResult`；如果没有，`GameState.lastResult` 也要可用。

### clear()

- 做什么：清空前端缓存的对局状态。
- 输入：无。
- 输出：清空 `gameState`、`lastTurnResult` 和错误信息。
- 后端能力：无直接要求。

## src/pages/index/index.vue

### goCreate()

- 做什么：跳转到房间页面。
- 输入：用户点击。
- 输出：页面导航到 `/pages/room/create`。
- 后端能力：房间页后续会承接创建、加入、开局接口。

### goBoard()

- 做什么：跳转到棋盘页面。
- 输入：用户点击“继续对局”。
- 输出：页面导航到 `/pages/game/board`。
- 后端能力：棋盘页必须能通过已保存的 `gameId` 拉取状态。

## src/pages/room/create.vue

### onMounted()

- 做什么：页面加载时把 session 中已有的 `roomId/gameId` 填回输入框。
- 输入：Pinia session。
- 输出：输入框默认值。
- 后端能力：无直接要求，但说明当前页面是联调辅助入口。

### saveSession()

- 做什么：把用户手动输入的 `roomId/gameId` 保存到本地 session。
- 输入：两个输入框中的文本。
- 输出：更新 session 并显示 toast。
- 后端能力：后端接口返回的 ID 应该方便复制到这里联调。

### goBoard()

- 做什么：检查是否存在 `gameId`，存在则进入棋盘页。
- 输入：当前 session。
- 输出：导航或 toast。
- 后端能力：`GET /api/games/:gameId` 是当前棋盘页唯一依赖。

## src/pages/game/board.vue

### refresh()

- 做什么：调用 `getGame(session.gameId)` 拉取后端状态。
- 输入：session 中的 `gameId`。
- 输出：成功时写入 game store，失败时显示错误消息。
- 后端能力：必须实现 `GET /api/games/:gameId`，并在失败时返回 `{ "message": "..." }`。

## src/types/game.ts

这个文件没有运行时函数，但它是后端响应形状的核心契约。后端首期必须返回这些关键结构：

- `GameState`：完整游戏聚合，包含房间、回合、棋盘、玩家、牌堆、最近结果和设置。
- `Player`：玩家资金、位置、破产状态、四项成长数值、储蓄目标、手牌、状态、统计和回合记忆。
- `Tile`：地块 ID、名称、类型、位置、消费金额、允许动作和图标。
- `GameDecks`：行动牌堆、被动事件牌堆、弃牌堆。
- `TurnResult`：一次操作的数值变化和消息摘要。
