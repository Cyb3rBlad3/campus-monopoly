# CampusMonopoly 前端（UniApp）建构计划

约定：**工程位于 `front_end/`**；**仅 H5 为当前默认目标**（`npm run dev:h5` / `npm run build:h5`）。规则与数值由后端计算，前端只渲染 `GameState` / `TurnResult`。

## 一、接口（与规则文档第十三节一致）

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/rooms` | 创建宿舍房间 |
| `POST` | `/api/rooms/:roomId/players` | 加入玩家 |
| `POST` | `/api/rooms/:roomId/start` | 开局 |
| `GET` | `/api/games/:gameId` | 拉取完整 `GameState` |
| `POST` | `/api/games/:gameId/roll` | 投骰与移动 |
| `POST` | `/api/games/:gameId/tile-action` | 地块行动 |
| `POST` | `/api/games/:gameId/use-card` | 使用行动牌 |
| `POST` | `/api/games/:gameId/end-turn` | 结束回合 |

写操作应返回更新后的 `GameState` 与可选 `TurnResult`。环境变量 `VITE_API_BASE_URL` 配置根地址。

## 二、建议后续页面拆分

1. 首页（已有）：入口与 API 基址提示。  
2. 房间流：调用 `rooms` / `players` / `start`，写入 `sessionStore`。  
3. 棋盘主界面：地图组件 + 根据 `GameState` 渲染棋子与当前回合。  
4. 操作区：仅展示后端允许的按钮（地块 `actions`、手牌等）。  
5. 结算页：根据 `status` 与后端字段展示。

## 三、素材与视觉

见仓库根目录 `CampusMonopoly_UI_Asset_Plan.md`，静态资源放在 `src/static/`。

---

详细规则仍以 `CampusMonopoly_Improved_Rules.md` 为准。
