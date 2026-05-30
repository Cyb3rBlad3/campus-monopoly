import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { GameState, TurnResult } from "../types/game";
import type { GameMutationResponse } from "../api/http";
import type { ApiResult } from "../api/http";
import {
  getGame,
  rollDice,
  tileAction,
  useCard,
  endTurn,
  startRoom,
} from "../api/game";

export const useGameStore = defineStore("game", () => {
  const gameState = ref<GameState | null>(null);
  const lastTurnResult = ref<TurnResult | null>(null);
  const loading = ref(false);
  const errorMessage = ref("");

  const currentPlayer = computed(() => {
    const gs = gameState.value;
    if (!gs) return null;
    return gs.players.find((p) => p.id === gs.currentPlayerId) ?? null;
  });

  function setFromResponse(gs: GameState, turn?: TurnResult | null) {
    gameState.value = gs;
    lastTurnResult.value = turn ?? gs.lastResult ?? null;
  }

  function clear() {
    gameState.value = null;
    lastTurnResult.value = null;
    errorMessage.value = "";
  }

  async function applyMutation(
    res: ApiResult<GameMutationResponse>
  ): Promise<boolean> {
    if (res.ok) {
      setFromResponse(res.data.gameState, res.data.turnResult ?? null);
      return true;
    }
    errorMessage.value = res.message;
    uni.showToast({ title: res.message, icon: "none" });
    return false;
  }

  async function refresh(gameId: string): Promise<boolean> {
    loading.value = true;
    errorMessage.value = "";
    const res = await getGame(gameId);
    loading.value = false;
    if (res.ok) {
      setFromResponse(res.data, null);
      return true;
    }
    errorMessage.value = res.message;
    return false;
  }

  async function startGame(
    roomId: string,
    playerId: string,
    deviceId: string
  ): Promise<boolean> {
    loading.value = true;
    errorMessage.value = "";
    const res = await startRoom(roomId, { playerId, deviceId });
    loading.value = false;
    return applyMutation(res);
  }

  async function roll(gameId: string, playerId: string): Promise<boolean> {
    loading.value = true;
    errorMessage.value = "";
    const res = await rollDice(gameId, { playerId });
    loading.value = false;
    return applyMutation(res);
  }

  async function doTileAction(
    gameId: string,
    playerId: string,
    action: string,
    extra?: { targetPlayerId?: string; amount?: number }
  ): Promise<boolean> {
    loading.value = true;
    errorMessage.value = "";
    const res = await tileAction(gameId, { playerId, action, ...extra });
    loading.value = false;
    return applyMutation(res);
  }

  async function playCard(
    gameId: string,
    playerId: string,
    cardId: string,
    targetPlayerId?: string
  ): Promise<boolean> {
    loading.value = true;
    errorMessage.value = "";
    const res = await useCard(gameId, {
      playerId,
      cardId,
      targetPlayerId,
    });
    loading.value = false;
    return applyMutation(res);
  }

  async function finishTurn(
    gameId: string,
    playerId: string
  ): Promise<boolean> {
    loading.value = true;
    errorMessage.value = "";
    const res = await endTurn(gameId, { playerId });
    loading.value = false;
    return applyMutation(res);
  }

  return {
    gameState,
    lastTurnResult,
    loading,
    errorMessage,
    currentPlayer,
    setFromResponse,
    clear,
    refresh,
    startGame,
    roll,
    doTileAction,
    playCard,
    finishTurn,
  };
});
