# 后端设计依据记录

本文档记录“前端证据 -> 需求推导 -> 设计决定”。它不是逐字内部思维链，而是可审计、可复盘的工程推导。

## app/main.py

### 前端证据

`front_end/src/api/http.ts` 会把 `VITE_API_BASE_URL` 与 `/api/...` 拼接，然后通过浏览器 H5 请求后端。

### 需求推导

后端需要一个 HTTP 应用入口，开启 CORS，并挂载 `/api` 路由。

### 设计决定

创建 `app/main.py`，负责 FastAPI 实例、CORS、异常处理、路由注册和 `GET /health`。

### 替代方案

没有把路由全部写在入口文件里，因为后续房间和游戏接口会变多，拆分模块更容易阅读。

## app/core/errors.py

### 前端证据

`src/api/http.ts` 在非 2xx 响应中优先读取响应体的 `message` 字段。

### 需求推导

后端所有业务错误都应该返回统一的 `{ "message": "..." }`。

### 设计决定

创建 `AppError` 和异常处理器，路由和服务层抛出业务错误时由 FastAPI 统一转换响应。

## app/db/models.py

### 前端证据

前端只需要完整 `GameState`，规则文档第十三节也说后端返回完整状态。

### 需求推导

首期不需要把每张牌、每个状态拆成很多表；保存完整快照能更快打通规则闭环。

### 设计决定

创建 `rooms`、`room_players`、`games` 三张表。`games.state_json` 保存完整 `GameState`。

### 替代方案

没有首期采用全关系化设计，因为卡牌、状态、事件的关系会快速膨胀，容易拖慢核心闭环。

## app/schemas/game.py

### 前端证据

`src/api/game.ts` 的写接口都传普通对象，前端还没有强类型请求体。

### 需求推导

后端需要先定义稳定请求体，让联调时知道每个字段含义。

### 设计决定

创建 Pydantic 请求模型：创建房间、加入玩家、掷骰、地块行动、用牌、结束回合。

## app/api/routes/rooms.py

### 前端证据

`src/api/game.ts` 定义了 `POST /api/rooms`、`POST /api/rooms/:roomId/players`、`POST /api/rooms/:roomId/start`。

### 需求推导

房间相关 HTTP 入口应集中管理。

### 设计决定

创建 `rooms.py`，只负责请求体校验和调用 `GameService`。

## app/api/routes/games.py

### 前端证据

`src/api/game.ts` 定义了 `GET /api/games/:gameId`、`roll`、`tile-action`、`use-card`、`end-turn`。

### 需求推导

对局读取和操作应集中到 games 路由下，与前端资源路径保持一致。

### 设计决定

创建 `games.py`，路由层不直接计算规则，只调用服务层。

## app/services/game_service.py

### 前端证据

写操作都要返回完整 `GameState` 和可选 `TurnResult`，而数据库保存的是快照。

### 需求推导

需要一个应用服务协调“读取数据库 -> 调用规则 -> 保存快照 -> 返回响应”。

### 设计决定

创建 `GameService`，把事务、持久化和规则调用集中起来。

## app/domain/seeds.py

### 前端证据

`src/types/game.ts` 需要 `board`、`decks`，规则文档列出了 16 个地块、16 张行动牌和 18 个被动事件。

### 需求推导

后端开局时必须生成棋盘和牌堆。

### 设计决定

创建 `seeds.py`，存放首期棋盘、卡牌、被动事件静态数据。

## app/domain/rules.py

### 前端证据

规则文档写明：后端负责计算规则并返回完整 `GameState`，前端不得自行计算兼职限制、数值变化、破产和胜负。

### 需求推导

规则计算必须集中，不应散落在路由函数里。

### 设计决定

创建 `rules.py`，实现初始化、掷骰、地块行动、用牌、结束回合等核心闭环。
