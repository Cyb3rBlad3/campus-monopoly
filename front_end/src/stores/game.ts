import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { GameState, TurnResult } from "../types/game";

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

  return {
    gameState,
    lastTurnResult,
    loading,
    errorMessage,
    currentPlayer,
    setFromResponse,
    clear,
  };
});
