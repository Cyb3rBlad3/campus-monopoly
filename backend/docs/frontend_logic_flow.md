# 前端功能逻辑梳理

## 总体结构

前端是 Vue 3 + TypeScript + uni-app H5。入口 `src/main.ts` 创建 Vue 应用并安装 Pinia。页面注册在 `src/pages.json` 中，目前有首页、房间页、棋盘页三页。

前端当前不是完整游戏客户端，而是一个联调壳：它已经声明了 API、类型和状态缓存方式，但页面只做到手动保存房间/对局 ID 与拉取 `GameState` 摘要。

## 首页流程

`src/pages/index/index.vue` 做三件事：

1. 展示产品名和 H5 标识。
2. 展示 `VITE_API_BASE_URL` 解析出的接口基址。
3. 提供两个入口：创建/加入房间、继续对局。

后端影响：本地服务建议固定为 `http://127.0.0.1:8000`，让首页能直接展示当前联调目标。

## 房间页流程

`src/pages/room/create.vue` 当前只是联调辅助页：

1. 页面加载时读取 Pinia session 中保存的 `roomId` 和 `gameId`。
2. 用户可以手动填写这两个 ID。
3. 点击保存后写回 session。
4. 点击进入棋盘页前只检查 `gameId` 是否存在。

后端影响：首期可以先用 Postman、curl 或测试脚本创建房间、加入玩家、开局，再把返回的 `gameId` 填进前端页面验证 `GET /api/games/:gameId`。

## 棋盘页流程

`src/pages/game/board.vue` 目前只做状态读取：

1. 从 session 读取 `gameId`。
2. 点击“拉取 GameState”后调用 `getGame(gameId)`。
3. 成功后调用 `game.setFromResponse(res.data, null)`。
4. 页面展示 `status`、`round`、`currentPlayerId`、玩家数量和最近消息。

后端影响：`GET /api/games/:gameId` 必须优先稳定。只要这个接口返回兼容 `GameState` 的 JSON，前端当前页面就能联调。

## 接口调用链

前端接口链路是：

`pages/*` -> `src/api/game.ts` -> `src/api/http.ts` -> `uni.request` -> 后端

其中 `game.ts` 决定路径，`http.ts` 决定返回包装。后端必须保持路径一致，并让错误响应带 `message`。

## 状态流

前端状态流是：

1. session store 保存 `roomId/gameId/localPlayerId`。
2. game store 保存完整 `GameState` 和最近 `TurnResult`。
3. 前端不直接修改金钱、位置、手牌、胜负等规则字段。
4. 所有规则结果以后端返回的完整 `GameState` 为准。

## 首期联调建议

1. 启动后端：`uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`。
2. 前端设置：`VITE_API_BASE_URL=http://127.0.0.1:8000`。
3. 调用后端创建房间、加入玩家、开局。
4. 把返回的 `roomId/gameId` 填入房间页。
5. 进入棋盘页拉取状态。
6. 调用掷骰、地块行动、用牌、结束回合接口后再次拉取，观察状态变化。
