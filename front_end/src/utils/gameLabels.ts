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
