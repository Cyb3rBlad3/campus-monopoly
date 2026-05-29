export function normalizePlayerName(name: string): string {
  return name.trim();
}

export function isSamePlayerName(a: string, b: string): boolean {
  return normalizePlayerName(a).toLowerCase() === normalizePlayerName(b).toLowerCase();
}

/** 昵称是否已被房间内其他玩家占用（不含自己） */
export function isNameTakenInRoom(
  playerNames: string[],
  candidate: string,
  selfName?: string
): boolean {
  const key = normalizePlayerName(candidate).toLowerCase();
  if (!key) return false;
  return playerNames.some((n) => {
    if (selfName && isSamePlayerName(n, selfName)) return false;
    return normalizePlayerName(n).toLowerCase() === key;
  });
}

export function findPlayerIdByName(
  players: { id: string; name: string }[],
  name: string
): string | undefined {
  return players.find((p) => isSamePlayerName(p.name, name))?.id;
}
