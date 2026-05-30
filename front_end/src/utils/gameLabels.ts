/** 后端首期已实现的行动牌 id */
export const SUPPORTED_ACTION_CARD_IDS = new Set([
  "card_action_group_buy_discount",
  "card_action_grant",
  "card_action_treat_milk_tea",
  "card_action_overtime_job",
  "card_action_resale",
  "card_action_budget",
]);

export const TILE_ACTION_LABELS: Record<string, string> = {
  part_time: "校园兼职",
  study: "图书馆学习",
  rest: "宿舍休息",
  social_interaction: "社交互动",
  deposit: "定期存款",
};

export const SAVING_GOAL_OPTIONS = [
  { value: "conservative", label: "保守目标（存 20%）" },
  { value: "standard", label: "标准目标（存 35%）" },
  { value: "challenge", label: "挑战目标（存 50%）" },
] as const;

export const ALLOWANCE_OPTIONS = [
  { value: 3000, label: "轻松局 3000 元" },
  { value: 2000, label: "标准局 2000 元" },
  { value: 1000, label: "生存局 1000 元" },
] as const;

export function tileIconPath(icon?: string): string {
  if (!icon) return "";
  return `/static/tiles/${icon}`;
}

export function actionCardIconPath(cardId: string): string {
  return `/static/cards/action/${cardId}.svg`;
}

export function passiveEventIconPath(eventId: string): string {
  const fileId = eventId.startsWith("event_")
    ? `card_${eventId}`
    : eventId;
  return `/static/cards/event/${fileId}.svg`;
}

export const ACTION_CARD_NAMES: Record<string, string> = {
  card_action_group_party: "发起团建聚会",
  card_action_birthday_party: "举办生日会",
  card_action_delivery_runner: "代取快递跑腿",
  card_action_group_buy_discount: "拼单省钱",
  card_action_dorm_purchase: "宿舍分摊采购",
  card_action_grant: "申请助学金",
  card_action_treat_milk_tea: "请客喝奶茶",
  card_action_overtime_job: "兼职加班",
  card_action_bulk_stock: "集体囤货",
  card_action_tutoring: "学霸辅导",
  card_action_resale: "闲置物品转卖",
  card_action_public_payment: "宿舍公摊缴费",
  card_action_forbid: "禁止",
  card_action_budget: "制定预算",
  card_action_meal_partner: "室友饭搭子",
  card_action_book_swap: "二手教材互换",
};

export const ACTION_CARD_DESCRIPTIONS: Record<string, string> = {
  card_action_group_party: "组织宿舍团建，增进室友感情（社交类，首期仅展示）。",
  card_action_birthday_party: "为同学庆生，分享蛋糕与红包（收入类，首期仅展示）。",
  card_action_delivery_runner: "帮同学代取快递赚跑腿费（收入类，首期仅展示）。",
  card_action_group_buy_discount: "发起拼单，下回合个人消费减半。",
  card_action_dorm_purchase: "宿舍集体采购日用品，分摊支出（支出类，首期仅展示）。",
  card_action_grant: "向学校申请助学金，获得 300 元补贴。",
  card_action_treat_milk_tea: "请客喝奶茶，自己扣 200 元，其他玩家各得 50 元。",
  card_action_overtime_job: "周末加班兼职，额外获得 400 元。",
  card_action_bulk_stock: "集体囤货省开支（储蓄类，首期仅展示）。",
  card_action_tutoring: "帮同学补课赚辅导费（收入类，首期仅展示）。",
  card_action_resale: "在闲鱼转卖闲置，获得 250 元。",
  card_action_public_payment: "帮室友垫付公摊费用（社交类，首期仅展示）。",
  card_action_forbid: "阻止对手行动（攻击类，首期仅展示）。",
  card_action_budget: "制定消费预算，接下来 2 回合个人消费减半。",
  card_action_meal_partner: "和室友拼饭省钱（社交类，首期仅展示）。",
  card_action_book_swap: "互换二手教材赚差价（收入类，首期仅展示）。",
};

export const PASSIVE_EVENT_NAMES: Record<string, string> = {
  event_found_meal_card: "捡到饭卡",
  event_lost_package: "快递丢失",
  event_exam_resit: "考试挂科补考",
  event_canteen_free: "食堂饭菜免单",
  event_lottery: "校园随机抽奖",
  event_utility_overrun: "水电费超支",
  event_found_change: "捡到校园零钱",
  event_online_return: "网购踩雷退货",
  event_library_fine: "图书馆占座被罚",
  event_part_time_bonus: "兼职额外奖励",
  event_meal_card_reissue: "饭卡遗失补办",
  event_scholarship_bonus: "奖学金附加奖励",
  event_roommate_pay: "室友帮忙代付",
  event_coupon: "校园消费券",
  event_club_recruit: "社团招新",
  event_class_meeting: "临时班会",
  event_budget_success: "预算执行成功",
  event_dorm_talk: "宿舍夜谈",
};

export const PASSIVE_EVENT_DESCRIPTIONS: Record<string, string> = {
  event_found_meal_card: "在食堂捡到无主饭卡，随机获得 80–200 元。",
  event_lost_package: "快递驿站通知包裹丢失，损失 150 元。",
  event_exam_resit: "挂科需补考，扣 200 元，成绩 -8，心情 -15，精力 -10，3 回合内不能兼职。",
  event_canteen_free: "食堂今日免单，消费减免（首期仅记录）。",
  event_lottery: "参与校园抽奖，获得 100 元。",
  event_utility_overrun: "宿舍水电费超支，额外支出 100 元。",
  event_found_change: "在操场捡到零钱，获得 50 元。",
  event_online_return: "网购商品踩雷退货，损失 100 元。",
  event_library_fine: "图书馆占座被罚，损失 50 元。",
  event_part_time_bonus: "兼职表现优秀获额外奖励（首期仅记录）。",
  event_meal_card_reissue: "饭卡遗失需补办，损失 30 元。",
  event_scholarship_bonus: "奖学金附加奖励，获得 50 元，成绩 +3，认知 +3。",
  event_roommate_pay: "室友帮忙代付账单（社交类，首期仅记录）。",
  event_coupon: "获得校园消费券（首期仅记录）。",
  event_club_recruit: "社团招新活动（社交类，首期仅记录）。",
  event_class_meeting: "临时召开班会（特殊事件，首期仅记录）。",
  event_budget_success: "预算执行良好，获得奖励（首期仅记录）。",
  event_dorm_talk: "宿舍夜谈增进感情（社交类，首期仅记录）。",
};

export const CARD_TYPE_LABELS: Record<string, string> = {
  social: "社交",
  income: "收入",
  saving: "储蓄",
  expense: "支出",
  attack: "攻击",
  positive: "好运",
  negative: "霉运",
  special: "特殊",
};

export interface CardRevealMeta {
  id: string;
  name: string;
  description: string;
  iconPath: string;
  typeLabel: string;
}

export function getActionCardMeta(cardId: string): CardRevealMeta {
  return {
    id: cardId,
    name: ACTION_CARD_NAMES[cardId] ?? cardId,
    description:
      ACTION_CARD_DESCRIPTIONS[cardId] ?? "校园行动牌，可在回合中使用。",
    iconPath: actionCardIconPath(cardId),
    typeLabel: "行动牌",
  };
}

export function getPassiveEventMeta(eventId: string): CardRevealMeta {
  return {
    id: eventId,
    name: PASSIVE_EVENT_NAMES[eventId] ?? eventId,
    description:
      PASSIVE_EVENT_DESCRIPTIONS[eventId] ??
      "校园被动事件，掷骰后自动触发。",
    iconPath: passiveEventIconPath(eventId),
    typeLabel: "被动事件",
  };
}
