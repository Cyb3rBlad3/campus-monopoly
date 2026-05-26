# CampusMonopoly 前端（UniApp · H5）

Vue 3 + Vite + TypeScript 的 [uni-app](https://uniapp.dcloud.net.cn/) 工程，默认面向 **H5** 部署与宿舍同屏联调。

## 常用命令

```bash
cd front_end
npm install
npm run dev:h5
```

浏览器访问终端里提示的本地地址（manifest 中 devServer 端口默认为 `5173`）。

```bash
npm run build:h5
```

产物在 `dist/build/h5`。

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `VITE_API_BASE_URL` | 后端 API 根地址，无尾部斜杠。开发环境见 `.env.development`，可复制 `.env.example`。 |

请求封装在 `src/api/http.ts`，会拼接为 `{base}{path}`，与规则文档中的 `/api/...` 路径一致。

## 目录说明

| 路径 | 作用 |
| --- | --- |
| `src/api/game.ts` | 创建房间、开局、`roll` / `tile-action` / `use-card` / `end-turn` 等接口方法 |
| `src/types/game.ts` | `GameState`、`TurnResult` 等与《CampusMonopoly_Improved_Rules.md》对齐的类型 |
| `src/stores/` | Pinia：`game` 对局状态，`session` 房间 / gameId |
| `src/pages/` | 首页、房间会话占位、棋盘页（演示 `GET /api/games/:gameId`） |

业务规则以后端返回为准，前端不计算胜负与数值。

## 相关文档

- 游戏规则与接口：`../CampusMonopoly_Improved_Rules.md`
- 建构计划：`UNIAPP_CONSTRUCTION_PLAN.md`
