import type { Player } from "../types/game";

/** 与 campus_board_v2.svg viewBox 一致 */
export const BOARD_VIEWBOX = { width: 1200, height: 900 };

/** 格子组 scale(0.78) 以棋盘中心 (600,450) 缩放后的锚点 */
export const TILE_ANCHORS: Record<number, { x: number; y: number }> = {
  0: { x: 256, y: 189 },
  1: { x: 415, y: 189 },
  2: { x: 608, y: 189 },
  3: { x: 776, y: 189 },
  4: { x: 943, y: 189 },
  5: { x: 943, y: 278 },
  6: { x: 943, y: 439 },
  7: { x: 943, y: 563 },
  8: { x: 943, y: 687 },
  9: { x: 776, y: 687 },
  10: { x: 608, y: 687 },
  11: { x: 415, y: 687 },
  12: { x: 256, y: 687 },
  13: { x: 256, y: 563 },
  14: { x: 256, y: 439 },
  15: { x: 256, y: 278 },
};

/** 棋盘中央信息区（百分比，相对 board-wrap） */
export const CENTER_HUB_RECT = {
  left: 24,
  top: 29,
  width: 52,
  height: 42,
};

const STACK_OFFSETS: Record<number, [number, number][]> = {
  2: [
    [-20, 0],
    [20, 0],
  ],
  3: [
    [-22, -6],
    [22, -6],
    [0, 14],
  ],
  4: [
    [-20, -10],
    [20, -10],
    [-20, 12],
    [20, 12],
  ],
};

export function getStackOffset(
  index: number,
  total: number
): { dx: number; dy: number } {
  if (total <= 1) return { dx: 0, dy: 0 };
  const preset = STACK_OFFSETS[Math.min(total, 4)] ?? STACK_OFFSETS[4];
  const [dx, dy] = preset[index % preset.length];
  return { dx, dy };
}

export function anchorToPercent(x: number, y: number): { left: string; top: string } {
  return {
    left: `${(x / BOARD_VIEWBOX.width) * 100}%`,
    top: `${(y / BOARD_VIEWBOX.height) * 100}%`,
  };
}

export interface PlayerMarkerLayout {
  player: Player;
  stackIndex: number;
  stackTotal: number;
  style: {
    left: string;
    top: string;
    zIndex: number;
  };
}

export function buildPlayerMarkers(players: Player[]): PlayerMarkerLayout[] {
  const active = players.filter((p) => !p.bankrupt);
  const byTile = new Map<number, Player[]>();

  for (const player of active) {
    const group = byTile.get(player.position) ?? [];
    group.push(player);
    byTile.set(player.position, group);
  }

  const markers: PlayerMarkerLayout[] = [];

  for (const [position, group] of byTile) {
    const anchor = TILE_ANCHORS[position];
    if (!anchor) continue;

    const sorted = [...group].sort((a, b) => a.id.localeCompare(b.id));
    sorted.forEach((player, index) => {
      const { dx, dy } = getStackOffset(index, sorted.length);
      const pct = anchorToPercent(anchor.x + dx, anchor.y + dy);
      markers.push({
        player,
        stackIndex: index,
        stackTotal: sorted.length,
        style: {
          left: pct.left,
          top: pct.top,
          zIndex: 10 + index,
        },
      });
    });
  }

  return markers;
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
