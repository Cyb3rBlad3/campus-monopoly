import { computed } from "vue";
import { useGameStore } from "../stores/game";
import { useSessionStore } from "../stores/session";
import { SUPPORTED_ACTION_CARD_IDS } from "../utils/gameLabels";
import type { Player, Tile } from "../types/game";

export function useGamePlay() {
  const game = useGameStore();
  const session = useSessionStore();

  const gameState = computed(() => game.gameState);

  const localPlayer = computed(() => {
    const gs = gameState.value;
    if (!gs || !session.localPlayerId) return null;
    return gs.players.find((p) => p.id === session.localPlayerId) ?? null;
  });

  const currentPlayer = computed(() => game.currentPlayer);

  const isMyTurn = computed(() => {
    const gs = gameState.value;
    return (
      !!gs &&
      gs.status === "playing" &&
      !!session.localPlayerId &&
      gs.currentPlayerId === session.localPlayerId
    );
  });

  const currentTile = computed((): Tile | null => {
    const gs = gameState.value;
    const cp = currentPlayer.value;
    if (!gs || !cp) return null;
    return gs.board[cp.position] ?? null;
  });

  const playableCards = computed(() => {
    const lp = localPlayer.value;
    if (!lp?.handCards?.length) return [];
    return lp.handCards.filter((c) => SUPPORTED_ACTION_CARD_IDS.has(c.id));
  });

  const canRoll = computed(() => {
    if (!isMyTurn.value) return false;
    const lp = localPlayer.value;
    const gs = gameState.value;
    return (
      !!lp &&
      !!gs &&
      gs.turnPhase === "awaiting_roll" &&
      !lp.turnFlags?.rolled
    );
  });

  const canTileAction = computed(() => {
    if (!isMyTurn.value) return false;
    const lp = localPlayer.value;
    const tile = currentTile.value;
    return (
      !!lp &&
      !!tile?.actions?.length &&
      lp.turnFlags?.rolled &&
      !lp.turnFlags?.tileActionUsed
    );
  });

  const canUseCard = computed(() => {
    if (!isMyTurn.value) return false;
    const lp = localPlayer.value;
    return (
      !!lp &&
      lp.turnFlags?.rolled &&
      !lp.turnFlags?.usedCard &&
      playableCards.value.length > 0
    );
  });

  const canEndTurn = computed(() => {
    if (!isMyTurn.value) return false;
    const lp = localPlayer.value;
    return !!lp && lp.turnFlags?.rolled;
  });

  const otherPlayers = computed((): Player[] => {
    const gs = gameState.value;
    if (!gs) return [];
    return gs.players.filter(
      (p) => p.id !== session.localPlayerId && !p.bankrupt
    );
  });

  return {
    gameState,
    localPlayer,
    currentPlayer,
    currentTile,
    isMyTurn,
    canRoll,
    canTileAction,
    canUseCard,
    canEndTurn,
    playableCards,
    otherPlayers,
  };
}
