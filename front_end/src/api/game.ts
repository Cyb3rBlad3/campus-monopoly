import { postJson, getJson, type GameMutationResponse } from "./http";
import type { GameState } from "../types/game";

export type CreateRoomBody = Record<string, unknown>;
export type JoinPlayerBody = Record<string, unknown>;
export type StartGameBody = Record<string, unknown>;

export function createRoom(body?: CreateRoomBody) {
  return postJson<GameState | { roomId: string }>("/api/rooms", body);
}

export function joinRoom(roomId: string, body?: JoinPlayerBody) {
  return postJson<GameMutationResponse>(
    `/api/rooms/${encodeURIComponent(roomId)}/players`,
    body
  );
}

export function startRoom(roomId: string, body?: StartGameBody) {
  return postJson<GameMutationResponse>(
    `/api/rooms/${encodeURIComponent(roomId)}/start`,
    body
  );
}

export function getGame(gameId: string) {
  return getJson<GameState>(
    `/api/games/${encodeURIComponent(gameId)}`
  );
}

export function rollDice(gameId: string, body?: Record<string, unknown>) {
  return postJson<GameMutationResponse>(
    `/api/games/${encodeURIComponent(gameId)}/roll`,
    body
  );
}

export function tileAction(
  gameId: string,
  body?: Record<string, unknown>
) {
  return postJson<GameMutationResponse>(
    `/api/games/${encodeURIComponent(gameId)}/tile-action`,
    body
  );
}

export function useCard(gameId: string, body?: Record<string, unknown>) {
  return postJson<GameMutationResponse>(
    `/api/games/${encodeURIComponent(gameId)}/use-card`,
    body
  );
}

export function endTurn(gameId: string, body?: Record<string, unknown>) {
  return postJson<GameMutationResponse>(
    `/api/games/${encodeURIComponent(gameId)}/end-turn`,
    body
  );
}
