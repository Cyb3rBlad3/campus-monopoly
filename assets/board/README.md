# CampusMonopoly 地图与棋盘素材

本目录包含第一批可用于数字原型的地图与棋盘 SVG 素材。

## 文件清单

| 文件 | 内容 |
| --- | --- |
| `campus_board.svg` | 1200x900 校园路线型棋盘，包含 16 个地块 |
| `player_pieces.svg` | 4 个玩家棋子，分别对应 P1-P4 |
| `dice_faces.svg` | 1-6 点静态骰子素材 |
| `dice_1.svg` - `dice_6.svg` | 拆分后的独立骰子素材 |
| `board_highlights.svg` | 当前地块、移动路径、当前玩家高亮素材 |
| `tile_grid_template.svg` | 收入、支出、社交、储蓄、特殊五类地块模板 |

## 风格说明

- 清爽扁平校园风。
- 主色使用校园绿和清爽蓝。
- 支出类地块使用柔和红色。
- 储蓄类地块使用暖黄色。
- 社交类地块使用浅蓝色。
- 特殊类地块使用浅紫色。

## 使用建议

- `campus_board.svg` 可直接作为主棋盘底图使用。
- 若前端需要单独控制棋子位置，可将 `player_pieces.svg` 中的 4 个 `g` 节点拆出为独立 SVG。
- 若需要动态投骰，可先使用 `dice_faces.svg` 的 6 个静态分组做帧切换。
- `board_highlights.svg` 中的高亮元素可改为 CSS 动画实现闪烁或路径流动效果。
