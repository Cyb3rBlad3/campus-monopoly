import { isSamePlayerName, normalizePlayerName } from "./playerName";

/** 内置 25 个 4～6 字中文短语昵称 */
export const PLAYER_NAME_DICTIONARY = [
  "早八赶课",
  "奶茶续命",
  "食堂抢饭",
  "期末复习",
  "宿舍开黑",
  "操场夜跑",
  "社团招新",
  "快递代取",
  "论文熬夜",
  "单车驰骋",
  "选课抢课",
  "勤工俭学",
  "校园漫步",
  "实验报告",
  "闲鱼二手",
  "球场挥洒",
  "琴房练琴",
  "泡面加餐",
  "毕业留影",
  "答辩准备",
  "实习打卡",
  "校巴通勤",
  "深夜自习",
  "图书馆占座",
  "周末睡到自然",
] as const;

export type DictionaryPlayerName = (typeof PLAYER_NAME_DICTIONARY)[number];

const DEFAULT_FALLBACK_NAME = "玩家";

export function isDictionaryPlayerName(name: string): boolean {
  const key = normalizePlayerName(name).toLowerCase();
  return PLAYER_NAME_DICTIONARY.some(
    (entry) => normalizePlayerName(entry).toLowerCase() === key
  );
}

function isNameUsed(name: string, usedNames: string[], selfName?: string): boolean {
  const key = normalizePlayerName(name).toLowerCase();
  if (!key) return false;
  return usedNames.some((used) => {
    if (selfName && isSamePlayerName(used, selfName)) return false;
    return normalizePlayerName(used).toLowerCase() === key;
  });
}

/** 从字典中随机挑选未被占用的昵称；用尽时追加两位数字后缀 */
export function pickRandomDictionaryName(
  usedNames: string[],
  selfName?: string
): string {
  const available = PLAYER_NAME_DICTIONARY.filter(
    (entry) => !isNameUsed(entry, usedNames, selfName)
  );
  if (available.length > 0) {
    return available[Math.floor(Math.random() * available.length)];
  }
  const base =
    PLAYER_NAME_DICTIONARY[
      Math.floor(Math.random() * PLAYER_NAME_DICTIONARY.length)
    ];
  const suffix = Math.floor(Math.random() * 90 + 10);
  return `${base}${suffix}`;
}

/**
 * 根据当前在线玩家已占用昵称，建议一个可用的字典昵称。
 * 若已有绑定/会话昵称且未被占用，则优先保留。
 */
export function suggestDictionaryPlayerName(
  usedNames: string[],
  options?: { preferredName?: string; selfName?: string }
): string {
  const preferred = normalizePlayerName(options?.preferredName ?? "");
  if (
    preferred &&
    preferred !== DEFAULT_FALLBACK_NAME &&
    !isNameUsed(preferred, usedNames, options?.selfName)
  ) {
    return preferred;
  }
  return pickRandomDictionaryName(usedNames, options?.selfName);
}

export function collectOnlinePlayerNames(
  rooms: { playerNames: string[] }[]
): string[] {
  return rooms.flatMap((room) => room.playerNames);
}
