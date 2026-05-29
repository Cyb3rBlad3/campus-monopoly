import type { GameState } from "./game";

export interface RoomSummary {
  roomId: string;
  gameId: string;
  status: string;
  maxPlayers: number;
  playerCount: number;
  initialAllowance: number;
  playerNames: string[];
  updatedAt?: string | null;
  expiresAt?: string | null;
  waitingTtlSeconds?: number;
  playerPresenceTtlSeconds?: number;
}

export interface PresenceResponse {
  ok: boolean;
  playerId: string;
}

export interface RejoinResponse {
  gameState: GameState;
  playerId: string;
  reconnected: boolean;
}
