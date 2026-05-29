from __future__ import annotations

from copy import deepcopy
from typing import Any


BOARD: list[dict[str, Any]] = [
    {
        "id": "tile_teaching_building",
        "name": "教学楼",
        "type": "income",
        "position": 0,
        "cost": 0,
        "actions": [],
        "icon": "tile_teaching_building.svg",
    },
    {
        "id": "tile_canteen",
        "name": "食堂",
        "type": "expense",
        "position": 1,
        "cost": 40,
        "actions": [],
        "icon": "tile_canteen.svg",
    },
    {
        "id": "tile_library",
        "name": "图书馆",
        "type": "income",
        "position": 2,
        "cost": 0,
        "actions": ["study"],
        "icon": "tile_library.svg",
    },
    {
        "id": "tile_supermarket",
        "name": "超市",
        "type": "expense",
        "position": 3,
        "cost": 60,
        "actions": [],
        "icon": "tile_supermarket.svg",
    },
    {
        "id": "tile_package_station",
        "name": "快递站",
        "type": "special",
        "position": 4,
        "cost": 0,
        "actions": [],
        "icon": "tile_package_station.svg",
    },
    {
        "id": "tile_milk_tea",
        "name": "奶茶店",
        "type": "expense",
        "position": 5,
        "cost": 50,
        "actions": [],
        "icon": "tile_milk_tea.svg",
    },
    {
        "id": "tile_takeout",
        "name": "外卖店",
        "type": "expense",
        "position": 6,
        "cost": 80,
        "actions": [],
        "icon": "tile_takeout.svg",
    },
    {
        "id": "tile_online_shop",
        "name": "网购点",
        "type": "expense",
        "position": 7,
        "cost": 150,
        "actions": [],
        "icon": "tile_online_shop.svg",
    },
    {
        "id": "tile_cinema",
        "name": "电影院",
        "type": "expense",
        "position": 8,
        "cost": 120,
        "actions": [],
        "icon": "tile_cinema.svg",
    },
    {
        "id": "tile_part_time_center",
        "name": "兼职中心",
        "type": "income",
        "position": 9,
        "cost": 0,
        "actions": ["part_time"],
        "icon": "tile_part_time_center.svg",
    },
    {
        "id": "tile_dormitory",
        "name": "宿舍",
        "type": "special",
        "position": 10,
        "cost": 0,
        "actions": ["rest"],
        "icon": "tile_dormitory.svg",
    },
    {
        "id": "tile_bank",
        "name": "银行",
        "type": "saving",
        "position": 11,
        "cost": 0,
        "actions": ["deposit"],
        "icon": "tile_bank.svg",
    },
    {
        "id": "tile_exam_site",
        "name": "考点",
        "type": "special",
        "position": 12,
        "cost": 100,
        "actions": [],
        "icon": "tile_exam_site.svg",
    },
    {
        "id": "tile_club_square",
        "name": "社团广场",
        "type": "social",
        "position": 13,
        "cost": 0,
        "actions": ["social_interaction"],
        "icon": "tile_club_square.svg",
    },
    {
        "id": "tile_wish_wall",
        "name": "心愿墙",
        "type": "saving",
        "position": 14,
        "cost": 0,
        "actions": [],
        "icon": "tile_wish_wall.svg",
    },
    {
        "id": "tile_dorm_meeting",
        "name": "宿舍议事厅",
        "type": "social",
        "position": 15,
        "cost": 0,
        "actions": [],
        "icon": "tile_dorm_meeting.svg",
    },
]


ACTION_CARDS: list[dict[str, Any]] = [
    {"id": "card_action_group_party", "name": "发起团建聚会", "type": "social"},
    {"id": "card_action_birthday_party", "name": "举办生日会", "type": "income"},
    {"id": "card_action_delivery_runner", "name": "代取快递跑腿", "type": "income"},
    {"id": "card_action_group_buy_discount", "name": "拼单省钱", "type": "saving"},
    {"id": "card_action_dorm_purchase", "name": "宿舍分摊采购", "type": "expense"},
    {"id": "card_action_grant", "name": "申请助学金", "type": "income"},
    {"id": "card_action_treat_milk_tea", "name": "请客喝奶茶", "type": "social"},
    {"id": "card_action_overtime_job", "name": "兼职加班", "type": "income"},
    {"id": "card_action_bulk_stock", "name": "集体囤货", "type": "saving"},
    {"id": "card_action_tutoring", "name": "学霸辅导", "type": "income"},
    {"id": "card_action_resale", "name": "闲置物品转卖", "type": "income"},
    {"id": "card_action_public_payment", "name": "宿舍公摊缴费", "type": "social"},
    {"id": "card_action_forbid", "name": "禁止", "type": "attack"},
    {"id": "card_action_budget", "name": "制定预算", "type": "saving"},
    {"id": "card_action_meal_partner", "name": "室友饭搭子", "type": "social"},
    {"id": "card_action_book_swap", "name": "二手教材互换", "type": "income"},
]


PASSIVE_EVENTS: list[dict[str, Any]] = [
    {"id": "event_found_meal_card", "name": "捡到饭卡", "type": "positive", "moneyRange": [80, 200]},
    {"id": "event_lost_package", "name": "快递丢失", "type": "negative", "money": -150},
    {
        "id": "event_exam_resit",
        "name": "考试挂科补考",
        "type": "negative",
        "money": -200,
        "grade": -8,
        "mood": -15,
        "energy": -10,
        "partTimeBlockedTurns": 3,
    },
    {"id": "event_canteen_free", "name": "食堂饭菜免单", "type": "positive"},
    {"id": "event_lottery", "name": "校园随机抽奖", "type": "positive", "money": 100},
    {"id": "event_utility_overrun", "name": "水电费超支", "type": "negative", "money": -100},
    {"id": "event_found_change", "name": "捡到校园零钱", "type": "positive", "money": 50},
    {"id": "event_online_return", "name": "网购踩雷退货", "type": "negative", "money": -100},
    {"id": "event_library_fine", "name": "图书馆占座被罚", "type": "negative", "money": -50},
    {"id": "event_part_time_bonus", "name": "兼职额外奖励", "type": "positive"},
    {"id": "event_meal_card_reissue", "name": "饭卡遗失补办", "type": "negative", "money": -30},
    {
        "id": "event_scholarship_bonus",
        "name": "奖学金附加奖励",
        "type": "positive",
        "money": 50,
        "grade": 3,
        "cognition": 3,
    },
    {"id": "event_roommate_pay", "name": "室友帮忙代付", "type": "social"},
    {"id": "event_coupon", "name": "校园消费券", "type": "positive"},
    {"id": "event_club_recruit", "name": "社团招新", "type": "social"},
    {"id": "event_class_meeting", "name": "临时班会", "type": "special"},
    {"id": "event_budget_success", "name": "预算执行成功", "type": "positive"},
    {"id": "event_dorm_talk", "name": "宿舍夜谈", "type": "social"},
]


def clone_board() -> list[dict[str, Any]]:
    return deepcopy(BOARD)


def clone_action_cards() -> list[dict[str, Any]]:
    return deepcopy(ACTION_CARDS)


def clone_passive_events() -> list[dict[str, Any]]:
    return deepcopy(PASSIVE_EVENTS)
