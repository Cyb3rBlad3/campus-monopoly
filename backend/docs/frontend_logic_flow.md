# 前端功能逻辑梳理

## 总体结构

前端是 Vue 3 + TypeScript + uni-app H5。入口 `src/main.ts` 创建 Vue 应用并安装 Pinia。页面注册在 `src/pages.json` 中，目前有首页、房间页、棋盘页三页。

前端已实现本地 2–4 人轮流的主玩法循环（房间创建/加入/开局、掷骰、地块行动、行动牌、结束回合），规则结果以后端 `GameState` 为准。

## 首页流程

`src/pages/index/index.vue` 做三件事：

1. 展示产品名和 H5 标识。
2. 展示 `VITE_API_BASE_URL` 解析出的接口基址。
3. 提供两个入口：创建/加入房间、继续对局。

后端影响：本地服务建议固定为 `http://127.0.0.1:8000`，让首页能直接展示当前联调目标。

## 房间页流程

`src/pages/room/create.vue` 为房间大厅：

1. 选择生活费档位、储蓄目标与昵称。
2. 创建房间后创建者自动加入；他人凭房间号加入。
3. ≥2 人时可调用 `startRoom` 开局并跳转棋盘。
4. session 通过 `uni.storage` 持久化 `roomId/gameId/localPlayerId`。

## 棋盘页流程

`src/pages/game/board.vue` 为对局主界面：

1. 展示棋盘底图、地块条、玩家资金与成长数值、回合日志。
2. 当前玩家回合内：掷骰 → 可选地块行动（兼职/学习/休息/社交/存款）→ 可选使用后端已实现的 6 张行动牌 → 结束回合。
3. 非当前玩家每 4 秒轮询 `getGame` 刷新状态（本地 pass-and-play）。
4. `status=finished` 时展示获胜者。

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
