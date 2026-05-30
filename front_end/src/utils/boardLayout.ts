import type { Player, Tile } from "../types/game";

export const BOARD_TILE_COUNT = 16;

/**
 * 5×5 棋盘格位置（1-based，对应 CSS grid-row / grid-column）。
 * 顺时针：顶 0–4 → 右 5–8 → 底 9–12 → 左 13–15
 *
 *  R1:  0   1   2   3   4
 *  R2: 15              5
 *  R3: 14      HUB     6
 *  R4: 13              7
 *  R5: 12  11  10   9   8
 */
export const TILE_GRID_CELL: Record<number, { row: number; col: number }> = {
  0: { row: 1, col: 1 },
  1: { row: 1, col: 2 },
  2: { row: 1, col: 3 },
  3: { row: 1, col: 4 },
  4: { row: 1, col: 5 },
  5: { row: 2, col: 5 },
  6: { row: 3, col: 5 },
  7: { row: 4, col: 5 },
  8: { row: 5, col: 5 },
  9: { row: 5, col: 4 },
  10: { row: 5, col: 3 },
  11: { row: 5, col: 2 },
  12: { row: 5, col: 1 },
  13: { row: 4, col: 1 },
  14: { row: 3, col: 1 },
  15: { row: 2, col: 1 },
};

export const TILE_TYPE_CLASS: Record<string, string> = {
  income: "tile--income",
  expense: "tile--expense",
  social: "tile--social",
  saving: "tile--saving",
  special: "tile--special",
};

export function normalizeBoardPosition(position: number): number {
  if (!Number.isFinite(position)) return 0;
  const n = Math.trunc(position);
  return ((n % BOARD_TILE_COUNT) + BOARD_TILE_COUNT) % BOARD_TILE_COUNT;
}

export function tileGridStyle(position: number): Record<string, string | number> {
  const cell = TILE_GRID_CELL[normalizeBoardPosition(position)];
  if (!cell) return {};
  return {
    gridRow: cell.row,
    gridColumn: cell.col,
  };
}

export function groupPlayersByTile(players: Player[]): Map<number, Player[]> {
  const map = new Map<number, Player[]>();
  for (const player of players) {
    if (player.bankrupt) continue;
    const pos = normalizeBoardPosition(player.position);
    const list = map.get(pos) ?? [];
    list.push(player);
    map.set(pos, list);
  }
  for (const [, list] of map) {
    list.sort((a, b) => a.id.localeCompare(b.id));
  }
  return map;
}

export function getTileByPosition(board: Tile[], position: number): Tile | undefined {
  const pos = normalizeBoardPosition(position);
  return board.find((t) => t.position === pos) ?? board[pos];
}

export const DEFAULT_PIECE_COLORS = [
  "#2e7d32",
  "#1565c0",
  "#ef6c00",
  "#6a1b9a",
];

export function resolvePieceColor(player: Player, playerIndex: number): string {
  if (player.pieceColor) return player.pieceColor;
  return DEFAULT_PIECE_COLORS[playerIndex % DEFAULT_PIECE_COLORS.length];
}

export function playerInitial(name: string): string {
  const trimmed = name.trim();
  return trimmed ? trimmed.charAt(0) : "?";
}

/** 同格多人时的 flex 偏移 class */
export function pieceStackClass(index: number, total: number): string {
  if (total <= 1) return "";
  return `piece--stack-${Math.min(total, 4)}-${index + 1}`;
}
