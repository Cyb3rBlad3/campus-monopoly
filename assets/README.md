# CampusMonopoly 游戏图标素材

清爽扁平校园风 SVG，与 [`assets/board/campus_board_v2.svg`](board/campus_board_v2.svg) 棋盘内嵌图标风格一致。

## 目录结构

| 目录 | 数量 | 说明 |
| --- | --- | --- |
| [`board/`](board/) | 棋盘、骰子、棋子、高亮 | 已有 |
| [`tiles/`](tiles/) | 16 | 地块图标，文件名与 `backend/app/domain/seeds.py` 中 `icon` 字段一致 |
| [`cards/action/`](cards/action/) | 16 | 行动牌卡面图标 |
| [`cards/event/`](cards/event/) | 18 | 被动事件卡面图标 |
| [`icons/stats/`](icons/stats/) | 6 | 玩家状态栏数值图标（P0/P1 核心） |

前端联调拷贝位于 [`front_end/src/static/`](../front_end/src/static/)（运行 `python assets/generate_icons.py` 会同步）。

## 重新生成

```bash
python assets/generate_icons.py
```

## 地块图标清单

- `tile_teaching_building.svg` — 教学楼
- `tile_canteen.svg` — 食堂
- `tile_library.svg` — 图书馆
- `tile_supermarket.svg` — 超市
- `tile_package_station.svg` — 快递站
- `tile_milk_tea.svg` — 奶茶店
- `tile_takeout.svg` — 外卖店
- `tile_online_shop.svg` — 网购点
- `tile_cinema.svg` — 电影院
- `tile_part_time_center.svg` — 兼职中心
- `tile_dormitory.svg` — 宿舍
- `tile_bank.svg` — 银行
- `tile_exam_site.svg` — 考点
- `tile_club_square.svg` — 社团广场
- `tile_wish_wall.svg` — 心愿墙
- `tile_dorm_meeting.svg` — 宿舍议事厅

## 被动事件 ID 对照

后端 `PASSIVE_EVENTS` 使用 `event_*` id，素材文件名为 `card_event_*.svg`：

| 后端 id | 素材文件 |
| --- | --- |
| `event_found_meal_card` | `card_event_found_meal_card.svg` |
| `event_lost_package` | `card_event_lost_package.svg` |
| `event_exam_resit` | `card_event_exam_resit.svg` |
| `event_canteen_free` | `card_event_canteen_free.svg` |
| `event_lottery` | `card_event_lottery.svg` |
| `event_utility_overrun` | `card_event_utility_overrun.svg` |
| `event_found_change` | `card_event_found_change.svg` |
| `event_online_return` | `card_event_online_return.svg` |
| `event_library_fine` | `card_event_library_fine.svg` |
| `event_part_time_bonus` | `card_event_part_time_bonus.svg` |
| `event_meal_card_reissue` | `card_event_meal_card_reissue.svg` |
| `event_scholarship_bonus` | `card_event_scholarship_bonus.svg` |
| `event_roommate_pay` | `card_event_roommate_pay.svg` |
| `event_coupon` | `card_event_coupon.svg` |
| `event_club_recruit` | `card_event_club_recruit.svg` |
| `event_class_meeting` | `card_event_class_meeting.svg` |
| `event_budget_success` | `card_event_budget_success.svg` |
| `event_dorm_talk` | `card_event_dorm_talk.svg` |

## 预览

在浏览器打开 [`board/preview.html`](board/preview.html) 查看棋盘、骰子与图标总览。
