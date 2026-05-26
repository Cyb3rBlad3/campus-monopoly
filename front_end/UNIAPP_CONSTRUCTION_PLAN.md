# CampusMonopoly 前端（UniApp）建构计划

本文档约定：**所有前端工程文件放在仓库根目录下的 `front_end/` 内**；**业务规则与数值一律以后端返回的 `GameState` / `TurnResult` 为准**，前端只做展示与交互，不实现规则引擎。后端接口由同事实现，对接时使用《CampusMonopoly_Improved_Rules.md》第十三节中的接口建议。

---

## 一、接口约定（与规则文档一致）

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/rooms` | 创建宿舍房间 |
| `POST` | `/api/rooms/:roomId/players` | 玩家加入房间 |
| `POST` | `/api/rooms/:roomId/start` | 开局，初始化游戏状态 |
| `GET` | `/api/games/:gameId` | 拉取完整 `GameState`（轮询或进入对局时） |
| `POST` | `/api/games/:gameId/roll` | 投骰、移动并触发地块与被动事件 |
| `POST` | `/api/games/:gameId/tile-action` | 兼职、学习、休息、储蓄、社交等地块行动 |
| `POST` | `/api/games/:gameId/use-card` | 使用行动牌 |
| `POST` | `/api/games/:gameId/end-turn` | 结束回合，结算余额宝、状态等 |

**关键约定**：上述写操作响应体应包含更新后的完整 `GameState` 与本次 `TurnResult`（结构见规则文档 JSON 示例）。前端根据 `messages`、数值 delta 等做 UI 反馈，**禁止**在前端自行计算破产、胜负、兼职可否、数值增减。

**环境配置**：在 `front_end` 内使用 `.env` 或 `manifest` / 独立 `config` 模块配置 `baseURL`（开发可指向同事提供的 Mock 或联调地址）。

---

## 二、UniApp 技术选型建议

| 项 | 建议 |
| --- | --- |
| 脚手架 | `vue create -p dcloudio/uni-preset-vue` 或官方 CLI，在 `front_end/` 下初始化 |
| 语法 | Vue 3 + `<script setup>`（与团队习惯一致即可） |
| 状态 | Pinia：`gameStore` 存 `GameState`，`sessionStore` 存 `roomId` / `gameId` / 本地玩家标识 |
| 请求 | `uni.request` 封装为 `src/api/http.ts`：统一 baseURL、错误码、`GameState` 反序列化 |
| 路由 | `pages.json`：首页 → 建房/加入 → 玩家设置 → 棋盘对局 → 结算 |

**多端**：若仅需 H5 宿舍同屏，可先 `h5`；若需小程序/App，注意静态资源路径与登录态（若后端后续加鉴权再补）。

---

## 三、目录结构（建议，均在 `front_end/` 下）

```
front_end/
├── src/
│   ├── api/              # rooms、games 各接口方法
│   ├── stores/           # Pinia
│   ├── types/            # GameState、Player、TurnResult 等与文档对齐的 TS 类型
│   ├── components/       # 棋盘格、玩家条、手牌、骰子、弹窗等
│   ├── pages/            # 与 pages.json 一一对应
│   ├── static/           # 图标占位（完整素材见 CampusMonopoly_UI_Asset_Plan.md）
│   └── utils/            # 防抖、回合提示文案拼接（不做规则计算）
├── manifest.json
├── pages.json
├── uni.scss              # 主题色：校园绿/蓝 + 金币暖黄 + 警示柔和红
└── package.json
```

---

## 四、页面与接口映射

| 页面（建议） | 主要调用的接口 |
| --- | --- |
| 首页 / 规则页 | 无（规则可内嵌 Markdown 转 HTML 或 WebView 读仓库文档） |
| 创建房间 | `POST /api/rooms` |
| 加入房间 + 玩家资料 | `POST /api/rooms/:roomId/players` |
| 开局前确认（生活费、储蓄目标等由后端字段约束） | `POST /api/rooms/:roomId/start` → 得到 `gameId` |
| 棋盘主界面 | `GET /api/games/:gameId`；操作中调用 `roll` / `tile-action` / `use-card` / `end-turn` |
| 结算 | 根据 `GameState.status` 与后端约定字段展示；可再次 `GET` 确保最终态 |

**交互顺序（与规则回合流程对齐，仅 UI 顺序）**：投骰 → 展示移动与 `TurnResult` → 被动事件弹窗 → 新手牌展示 → 可选使用行动牌 → 地块允许的操作按钮（由 `board` + 当前格 `actions` 驱动）→ 结束回合。

---

## 五、与《UI 素材清单》的对应关系

实现阶段按 `CampusMonopoly_UI_Asset_Plan.md` 的优先级：

- **P0**：开始页、房间创建、玩家设置、主棋盘、状态栏、骰子、手牌区、基础事件弹窗。
- **P1**：银行、共同基金、社交互动（邀请/互助/团建选择）、状态图标、数值反馈。
- **P2**：结算徽章、动效。

素材可先占位图，命名遵循该文档第十一节。

---

## 六、开发阶段划分（不含日历估算）

1. **工程初始化**：UniApp 项目落在 `front_end/`，TS 类型从规则文档第十三节抄齐并随后端微调字段。
2. **API 层**：封装 8 个接口，Mock 或直连同事环境；统一错误与 loading。
3. **房间流**：创建 → 加入 → 开局，持久化 `gameId`（`uni.setStorage`）。
4. **对局壳**：棋盘布局 + 根据 `GameState` 渲染棋子位置、`currentPlayerId`、回合信息。
5. **操作面板**：按钮可用性由后端返回的 `actions`、手牌 `requirements` 等字段决定（前端只做禁用态，不推导规则）。
6. **反馈层**：`TurnResult.messages` 列表、Toast/弹窗、简单动画。
7. **联调与收尾**：空状态、断线重连（定时 `GET`）、结算页。

---

## 七、相关文档索引

- 游戏规则与数据结构、接口：`/CampusMonopoly_Improved_Rules.md`
- 界面与素材：`/CampusMonopoly_UI_Asset_Plan.md`

---

*后端未在本仓库实现时，可在 `front_end` 内用 JSON 静态文件或 MSW 做最小演示，联调时切换 baseURL。*
