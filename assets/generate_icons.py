#!/usr/bin/env python3
"""Generate missing CampusMonopoly SVG icons (tiles, cards, stats)."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TILES_DIR = ROOT / "tiles"
ACTION_DIR = ROOT / "cards" / "action"
EVENT_DIR = ROOT / "cards" / "event"
STATS_DIR = ROOT / "icons" / "stats"
STATIC_ROOT = ROOT.parent / "front_end" / "src" / "static"

STROKE_DEFAULT = "#2c7a67"
STROKE_RED = "#cf6f61"
STROKE_BLUE = "#4f7fb8"
STROKE_YELLOW = "#b98714"
STROKE_PURPLE = "#7b64b6"

ICON_STYLE = (
    'fill="none" stroke-width="6" stroke-linecap="round" '
    'stroke-linejoin="round"'
)


def svg_icon(title: str, paths: list[tuple[str, str]], view_box: str = "0 0 120 120") -> str:
    body = "\n  ".join(
        f'<path {ICON_STYLE} stroke="{color}" d="{d}"/>' for color, d in paths
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img" aria-labelledby="title">
  <title id="title">{title}</title>
  {body}
</svg>
"""


def svg_card(title: str, paths: list[tuple[str, str]], accent: str, card_type: str) -> str:
    """96x128 card face with icon and type accent bar."""
    body = "\n    ".join(
        f'<path {ICON_STYLE} stroke="{color}" d="{d}"/>' for color, d in paths
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 128" role="img" aria-labelledby="title">
  <title id="title">{title}</title>
  <rect width="96" height="128" rx="12" fill="#ffffff" stroke="#d2e2dc" stroke-width="3"/>
  <rect x="0" y="0" width="96" height="18" rx="12" fill="{accent}"/>
  <rect x="0" y="10" width="96" height="8" fill="{accent}"/>
  <g transform="translate(8 28)">
    {body}
  </g>
  <text x="48" y="118" text-anchor="middle" font-family="Microsoft YaHei, Noto Sans SC, Arial, sans-serif" font-size="11" font-weight="700" fill="#657a74">{card_type}</text>
</svg>
"""


TILES: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "tile_teaching_building.svg",
        "教学楼",
        [(STROKE_DEFAULT, "M51 57 h68 M61 57 V31 h48 v26 M74 57 V43 h22 v14")],
    ),
    (
        "tile_canteen.svg",
        "食堂",
        [(STROKE_RED, "M57 30 v36 M76 30 v36 M57 48 h19 M108 30 c20 17 20 39 0 56")],
    ),
    (
        "tile_library.svg",
        "图书馆",
        [
            (
                STROKE_DEFAULT,
                "M49 34 c21 -9 36 -4 37 8 v38 c-13 -10 -27 -13 -37 -7 z "
                "M86 42 c1 -12 16 -17 37 -8 v39 c-10 -6 -24 -3 -37 7 z",
            )
        ],
    ),
    (
        "tile_supermarket.svg",
        "超市",
        [(STROKE_RED, "M52 38 h70 l-10 34 H63 z M66 84 h2 M104 84 h2 M58 38 l-7 -15")],
    ),
    (
        "tile_package_station.svg",
        "快递站",
        [
            (
                STROKE_BLUE,
                "M52 40 l33 -15 33 15 v38 l-33 15 -33 -15 z M52 40 l33 15 33 -15 M85 55 v38",
            )
        ],
    ),
    (
        "tile_milk_tea.svg",
        "奶茶店",
        [(STROKE_RED, "M62 36 h46 l-8 49 H70 z M74 36 l-6 -18 M73 65 h4 M87 71 h4 M101 61 h4")],
    ),
    (
        "tile_takeout.svg",
        "外卖店",
        [(STROKE_RED, "M58 49 h54 l-6 37 H64 z M70 49 c0 -18 30 -18 30 0 M51 34 h68")],
    ),
    (
        "tile_online_shop.svg",
        "网购点",
        [(STROKE_RED, "M64 27 h42 v61 H64 z M77 77 h16 M70 40 h30 M74 55 h22")],
    ),
    (
        "tile_cinema.svg",
        "电影院",
        [
            (
                STROKE_BLUE,
                "M53 38 h64 v43 H53 z M65 38 v43 M105 38 v43 M53 53 h64 M53 67 h64",
            )
        ],
    ),
    (
        "tile_part_time_center.svg",
        "兼职中心",
        [(STROKE_DEFAULT, "M58 44 h54 v38 H58 z M72 44 v-11 h26 v11 M73 64 h24")],
    ),
    (
        "tile_dormitory.svg",
        "宿舍",
        [(STROKE_BLUE, "M53 81 V43 l32 -20 32 20 v38 M72 81 V58 h26 v23")],
    ),
    (
        "tile_bank.svg",
        "银行",
        [(STROKE_YELLOW, "M52 52 h66 M61 52 v31 M80 52 v31 M99 52 v31 M52 83 h66 M85 28 l37 24 H48 z")],
    ),
    (
        "tile_exam_site.svg",
        "考点",
        [(STROKE_PURPLE, "M62 25 h46 v60 H62 z M73 42 h24 M73 56 h24 M73 70 h14")],
    ),
    (
        "tile_club_square.svg",
        "社团广场",
        [
            (
                STROKE_BLUE,
                "M52 76 c8 -19 26 -19 34 0 M80 76 c8 -19 26 -19 34 0 "
                "M67 43 a10 10 0 1 0 0 1 M96 43 a10 10 0 1 0 0 1",
            )
        ],
    ),
    (
        "tile_wish_wall.svg",
        "心愿墙",
        [(STROKE_YELLOW, "M60 30 h50 v43 H77 l-17 14 V30 z M77 52 h16 M85 44 v16")],
    ),
    (
        "tile_dorm_meeting.svg",
        "宿舍议事厅",
        [(STROKE_BLUE, "M52 58 c20 -22 46 -22 66 0 M65 77 h40 M59 46 h52 M73 33 h24")],
    ),
]

CARD_ACCENTS = {
    "social": "#7eb8e8",
    "income": "#6dbf9a",
    "saving": "#e8c45c",
    "expense": "#e89a8f",
    "attack": "#c97b9a",
    "positive": "#6dbf9a",
    "negative": "#e89a8f",
    "special": "#b39ddb",
}

ACTION_CARDS: list[tuple[str, str, str, list[tuple[str, str]]]] = [
    (
        "card_action_group_party.svg",
        "发起团建聚会",
        "social",
        [
            (STROKE_BLUE, "M18 52 c6 -14 20 -14 26 0 M44 52 c6 -14 20 -14 26 0"),
            (STROKE_BLUE, "M31 30 a8 8 0 1 0 0 1 M57 30 a8 8 0 1 0 0 1"),
            (STROKE_BLUE, "M52 58 h18 l-6 22 H46 z"),
        ],
    ),
    (
        "card_action_birthday_party.svg",
        "举办生日会",
        "income",
        [
            (STROKE_DEFAULT, "M40 70 h40 v-18 c0 -16 -40 -16 -40 0 z"),
            (STROKE_YELLOW, "M48 38 l4 -10 4 10 M56 40 l3 -8 3 8"),
        ],
    ),
    (
        "card_action_delivery_runner.svg",
        "代取快递跑腿",
        "income",
        [
            (STROKE_BLUE, "M20 38 l24 -12 24 12 v28 l-24 12 -24 -12 z"),
            (STROKE_DEFAULT, "M62 30 l14 8 M62 38 l18 4"),
        ],
    ),
    (
        "card_action_group_buy_discount.svg",
        "拼单省钱",
        "saving",
        [
            (STROKE_YELLOW, "M28 34 h36 l-8 32 H36 z"),
            (STROKE_YELLOW, "M52 28 l10 6 M52 36 l14 2"),
            (STROKE_YELLOW, "M58 48 h20 M64 42 v12"),
        ],
    ),
    (
        "card_action_dorm_purchase.svg",
        "宿舍分摊采购",
        "expense",
        [
            (STROKE_RED, "M30 36 h40 l-6 30 H36 z"),
            (STROKE_RED, "M22 52 h10 M68 52 h10"),
            (STROKE_RED, "M44 24 v8 M52 24 v8"),
        ],
    ),
    (
        "card_action_grant.svg",
        "申请助学金",
        "income",
        [
            (STROKE_DEFAULT, "M28 30 h48 v44 H28 z M28 42 h48"),
            (STROKE_YELLOW, "M44 54 h16 M52 46 v16"),
        ],
    ),
    (
        "card_action_treat_milk_tea.svg",
        "请客喝奶茶",
        "social",
        [
            (STROKE_RED, "M36 28 h32 l-6 38 H42 z"),
            (STROKE_RED, "M48 28 l-4 -12"),
            (STROKE_RED, "M58 44 c-6 6 -14 6 -20 0"),
        ],
    ),
    (
        "card_action_overtime_job.svg",
        "兼职加班",
        "income",
        [
            (STROKE_DEFAULT, "M32 34 h40 v36 H32 z M40 34 v-8 h24 v8"),
            (STROKE_DEFAULT, "M56 52 a14 14 0 1 0 0 1 M56 52 l8 -6"),
        ],
    ),
    (
        "card_action_bulk_stock.svg",
        "集体囤货",
        "saving",
        [
            (STROKE_YELLOW, "M24 48 h24 v24 H24 z M48 40 h24 v32 H48 z"),
            (STROKE_YELLOW, "M28 44 h16 M52 36 h16"),
        ],
    ),
    (
        "card_action_tutoring.svg",
        "学霸辅导",
        "income",
        [
            (STROKE_DEFAULT, "M28 36 c16 -8 28 -4 28 8 v32 c-12 -8 -22 -10 -28 -6 z"),
            (STROKE_BLUE, "M60 44 c0 -10 14 -14 26 -6 v20 c-8 -4 -18 -2 -26 4 z"),
            (STROKE_BLUE, "M62 28 c8 -6 18 -4 20 6"),
        ],
    ),
    (
        "card_action_resale.svg",
        "闲置物品转卖",
        "income",
        [
            (STROKE_DEFAULT, "M44 30 h28 v36 H44 z"),
            (STROKE_DEFAULT, "M36 52 a16 16 0 1 1 0 -1"),
            (STROKE_DEFAULT, "M52 44 l12 -8 M52 52 l12 8"),
        ],
    ),
    (
        "card_action_public_payment.svg",
        "宿舍公摊缴费",
        "social",
        [
            (STROKE_BLUE, "M28 32 h48 v40 H28 z M36 44 h32 M36 56 h24"),
            (STROKE_BLUE, "M52 24 v8 l16 10 H36 z"),
        ],
    ),
    (
        "card_action_forbid.svg",
        "禁止",
        "attack",
        [
            (STROKE_RED, "M48 24 a28 28 0 1 0 0 1"),
            (STROKE_RED, "M32 32 l48 48"),
        ],
    ),
    (
        "card_action_budget.svg",
        "制定预算",
        "saving",
        [
            (STROKE_YELLOW, "M26 30 h52 v48 H26 z M34 42 h12 M34 54 h12 M34 66 h12"),
            (STROKE_YELLOW, "M50 42 h20 M50 54 h16 M50 66 h10"),
        ],
    ),
    (
        "card_action_meal_partner.svg",
        "室友饭搭子",
        "social",
        [
            (STROKE_BLUE, "M24 48 h28 v20 H24 z M44 40 h28 v28 H44 z"),
            (STROKE_BLUE, "M30 44 h16 M50 36 h16"),
        ],
    ),
    (
        "card_action_book_swap.svg",
        "二手教材互换",
        "income",
        [
            (STROKE_DEFAULT, "M24 36 c12 -6 20 -2 20 8 v32 c-8 -6 -16 -8 -20 -4 z"),
            (STROKE_DEFAULT, "M52 40 c12 -6 20 -2 20 8 v32 c-8 -6 -16 -8 -20 -4 z"),
            (STROKE_BLUE, "M44 52 l16 0 M52 44 l0 16"),
        ],
    ),
]

PASSIVE_EVENTS: list[tuple[str, str, str, list[tuple[str, str]]]] = [
    (
        "card_event_found_meal_card.svg",
        "捡到饭卡",
        "positive",
        [
            (STROKE_YELLOW, "M32 34 h40 v36 H32 z"),
            (STROKE_YELLOW, "M40 46 h24 M48 58 h8"),
            (STROKE_DEFAULT, "M68 28 l8 8 M72 24 l4 12"),
        ],
    ),
    (
        "card_event_lost_package.svg",
        "快递丢失",
        "negative",
        [
            (STROKE_RED, "M28 40 l24 -12 24 12 v24 l-24 12 -24 -12 z"),
            (STROKE_RED, "M40 52 l16 16 M56 52 l-16 16"),
        ],
    ),
    (
        "card_event_exam_resit.svg",
        "考试挂科补考",
        "negative",
        [(STROKE_PURPLE, "M36 28 h40 v48 H36 z"), (STROKE_RED, "M44 44 l24 24 M68 44 l-24 24")],
    ),
    (
        "card_event_canteen_free.svg",
        "食堂饭菜免单",
        "positive",
        [
            (STROKE_DEFAULT, "M36 32 v28 M48 32 v28 M36 44 h12"),
            (STROKE_YELLOW, "M58 48 h28 c0 14 -28 14 -28 0"),
        ],
    ),
    (
        "card_event_lottery.svg",
        "校园随机抽奖",
        "positive",
        [(STROKE_YELLOW, "M32 36 h48 v32 H32 z M40 28 h32 v8 H40 z"), (STROKE_YELLOW, "M44 48 h8")],
    ),
    (
        "card_event_utility_overrun.svg",
        "水电费超支",
        "negative",
        [
            (STROKE_BLUE, "M40 28 c0 20 -8 32 -8 44"),
            (STROKE_RED, "M52 32 h32 v40 H52 z M60 44 h16 M60 56 h12"),
        ],
    ),
    (
        "card_event_found_change.svg",
        "捡到校园零钱",
        "positive",
        [
            (STROKE_YELLOW, "M48 28 a20 20 0 1 0 0 1"),
            (STROKE_YELLOW, "M48 40 v8"),
        ],
    ),
    (
        "card_event_online_return.svg",
        "网购踩雷退货",
        "negative",
        [
            (STROKE_RED, "M36 30 h40 v44 H36 z"),
            (STROKE_RED, "M28 52 l12 -8 v16 z M68 44 l12 8 v-16 z"),
        ],
    ),
    (
        "card_event_library_fine.svg",
        "图书馆占座被罚",
        "negative",
        [
            (STROKE_DEFAULT, "M32 44 c16 -8 28 -4 28 8 v28 c-12 -8 -22 -10 -28 -6 z"),
            (STROKE_RED, "M64 36 h16 v24 H64 z M68 40 h8"),
        ],
    ),
    (
        "card_event_part_time_bonus.svg",
        "兼职额外奖励",
        "positive",
        [
            (STROKE_DEFAULT, "M32 34 h40 v36 H32 z M40 34 v-8 h24 v8"),
            (STROKE_YELLOW, "M56 28 l6 10 10 -4 -4 10 10 4 -12 2 2 12"),
        ],
    ),
    (
        "card_event_meal_card_reissue.svg",
        "饭卡遗失补办",
        "negative",
        [
            (STROKE_YELLOW, "M32 34 h40 v36 H32 z"),
            (STROKE_RED, "M60 48 h16 M68 40 v16"),
        ],
    ),
    (
        "card_event_scholarship_bonus.svg",
        "奖学金附加奖励",
        "positive",
        [
            (STROKE_YELLOW, "M48 26 l8 16 18 2 -13 12 4 18 -17 -10 -17 10 4 -18"),
            (STROKE_DEFAULT, "M36 58 c12 -6 20 -2 20 8 v16 c-8 -6 -16 -8 -20 -4 z"),
        ],
    ),
    (
        "card_event_roommate_pay.svg",
        "室友帮忙代付",
        "social",
        [
            (STROKE_BLUE, "M24 50 c6 -12 18 -12 24 0 M52 50 c6 -12 18 -12 24 0"),
            (STROKE_YELLOW, "M40 62 h32 v12 H40 z M52 58 v20"),
        ],
    ),
    (
        "card_event_coupon.svg",
        "校园消费券",
        "positive",
        [
            (STROKE_YELLOW, "M28 36 h52 v28 H28 z M40 28 v44"),
            (STROKE_YELLOW, "M48 44 h20 M48 52 h14"),
        ],
    ),
    (
        "card_event_club_recruit.svg",
        "社团招新",
        "social",
        [
            (STROKE_BLUE, "M32 56 l16 -28 16 28 z"),
            (STROKE_BLUE, "M28 56 h48"),
            (STROKE_BLUE, "M40 44 h16"),
        ],
    ),
    (
        "card_event_class_meeting.svg",
        "临时班会",
        "special",
        [
            (STROKE_PURPLE, "M32 32 h48 v12 H32 z"),
            (STROKE_PURPLE, "M40 52 h32 v8 H40 z M48 44 v24"),
        ],
    ),
    (
        "card_event_budget_success.svg",
        "预算执行成功",
        "positive",
        [
            (STROKE_YELLOW, "M28 30 h52 v44 H28 z"),
            (STROKE_DEFAULT, "M40 52 l10 10 22 -24"),
        ],
    ),
    (
        "card_event_dorm_talk.svg",
        "宿舍夜谈",
        "social",
        [
            (STROKE_BLUE, "M32 48 h48 v24 H32 z M40 40 h16 v8"),
            (STROKE_BLUE, "M44 56 c8 8 16 8 24 0 M52 64 c8 8 16 8 24 0"),
        ],
    ),
]

STATS: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("stat_money.svg", "资金", [(STROKE_YELLOW, "M60 28 a24 24 0 1 0 0 1 M60 52 v8")]),
    (
        "stat_social.svg",
        "社交值",
        [
            (
                STROKE_BLUE,
                "M38 68 c8 -18 24 -18 32 0 M70 68 c8 -18 24 -18 32 0 "
                "M54 38 a10 10 0 1 0 0 1 M86 38 a10 10 0 1 0 0 1",
            )
        ],
    ),
    (
        "stat_finance.svg",
        "理财值",
        [
            (STROKE_YELLOW, "M32 72 L52 48 L72 60 L96 32"),
            (STROKE_YELLOW, "M32 72 h64"),
        ],
    ),
    (
        "stat_action_cards.svg",
        "行动牌",
        [
            (STROKE_DEFAULT, "M36 32 h48 v56 H36 z"),
            (STROKE_DEFAULT, "M44 24 h48 v56 H44 z"),
            (STROKE_DEFAULT, "M52 16 h48 v56 H52 z"),
        ],
    ),
    (
        "stat_common_fund.svg",
        "共同基金",
        [
            (STROKE_YELLOW, "M48 32 h48 v40 H48 z M40 40 h8"),
            (STROKE_BLUE, "M32 56 c6 -10 16 -10 22 0 M70 56 c6 -10 16 -10 22 0"),
        ],
    ),
    (
        "stat_saving_goal.svg",
        "储蓄目标",
        [
            (STROKE_YELLOW, "M60 28 a26 26 0 1 0 0 1"),
            (STROKE_YELLOW, "M60 40 a14 14 0 1 0 0 1"),
            (STROKE_YELLOW, "M60 52 a4 4 0 1 0 0 1"),
        ],
    ),
]


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for filename, title, paths in TILES:
        write_file(TILES_DIR / filename, svg_icon(title, paths))

    for filename, title, card_type, paths in ACTION_CARDS:
        write_file(
            ACTION_DIR / filename,
            svg_card(title, paths, CARD_ACCENTS[card_type], card_type),
        )

    for filename, title, card_type, paths in PASSIVE_EVENTS:
        write_file(
            EVENT_DIR / filename,
            svg_card(title, paths, CARD_ACCENTS[card_type], card_type),
        )

    for filename, title, paths in STATS:
        write_file(STATS_DIR / filename, svg_icon(title, paths))

    # Mirror into uni-app static folder
    if STATIC_ROOT.parent.exists():
        STATIC_ROOT.mkdir(parents=True, exist_ok=True)
        for name, src_dir in [
            ("tiles", TILES_DIR),
            ("cards/action", ACTION_DIR),
            ("cards/event", EVENT_DIR),
            ("icons/stats", STATS_DIR),
        ]:
            dest = STATIC_ROOT / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src_dir, dest)

        board_static = STATIC_ROOT / "board"
        board_static.mkdir(parents=True, exist_ok=True)
        board_src = ROOT / "board"
        for f in board_src.glob("*.svg"):
            shutil.copy2(f, board_static / f.name)

    counts = {
        "tiles": len(TILES),
        "action_cards": len(ACTION_CARDS),
        "passive_events": len(PASSIVE_EVENTS),
        "stats": len(STATS),
    }
    print("Generated:", counts)


if __name__ == "__main__":
    main()
