import { ref, computed, watch, onUnmounted } from "vue";
import { storeToRefs } from "pinia";
import { useGameStore } from "../stores/game";
import type { TurnResult } from "../types/game";
import {
  getActionCardMeta,
  getPassiveEventMeta,
  type CardRevealMeta,
} from "../utils/gameLabels";

export type RevealPhase = "idle" | "dice" | "passive" | "card" | "done";

const DICE_DURATION_MS = 1200;
const STEP_DURATION_MS = 1500;
const SESSION_SEEN_KEY = "campus_monopoly_turn_reveal_seen";

export interface TurnRevealData {
  playerName: string;
  dice: number;
  passiveMeta: CardRevealMeta | null;
  cardMeta: CardRevealMeta | null;
  stepIndex: number;
  stepTotal: number;
}

function turnResultFingerprint(result: TurnResult): string {
  return [
    result.playerId,
    result.dice,
    result.fromPosition,
    result.toPosition,
    result.triggeredEventId ?? "",
    result.drawnCardId ?? "",
  ].join(":");
}

function loadSeenKeys(): Set<string> {
  try {
    const raw = sessionStorage.getItem(SESSION_SEEN_KEY);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw) as string[];
    return new Set(Array.isArray(parsed) ? parsed : []);
  } catch {
    return new Set();
  }
}

function persistSeenKeys(keys: Set<string>) {
  try {
    sessionStorage.setItem(
      SESSION_SEEN_KEY,
      JSON.stringify([...keys].slice(-50))
    );
  } catch {
    /* ignore quota errors */
  }
}

export function useTurnReveal() {
  const game = useGameStore();
  const { lastTurnResult, gameState } = storeToRefs(game);

  const revealPhase = ref<RevealPhase>("idle");
  const revealData = ref<TurnRevealData | null>(null);
  const seenKeys = loadSeenKeys();
  let stepTimer: ReturnType<typeof setTimeout> | null = null;
  let diceTimer: ReturnType<typeof setTimeout> | null = null;

  function clearTimers() {
    if (stepTimer) {
      clearTimeout(stepTimer);
      stepTimer = null;
    }
    if (diceTimer) {
      clearTimeout(diceTimer);
      diceTimer = null;
    }
  }

  function resolvePlayerName(playerId: string): string {
    return (
      gameState.value?.players.find((p) => p.id === playerId)?.name ?? "玩家"
    );
  }

  function buildSteps(result: TurnResult): RevealPhase[] {
    const steps: RevealPhase[] = ["dice"];
    if (result.triggeredEventId) steps.push("passive");
    if (result.drawnCardId) steps.push("card");
    return steps;
  }

  function buildRevealData(result: TurnResult): TurnRevealData {
    const steps = buildSteps(result);
    return {
      playerName: resolvePlayerName(result.playerId),
      dice: result.dice,
      passiveMeta: result.triggeredEventId
        ? getPassiveEventMeta(result.triggeredEventId)
        : null,
      cardMeta: result.drawnCardId
        ? getActionCardMeta(result.drawnCardId)
        : null,
      stepIndex: 1,
      stepTotal: steps.length,
    };
  }

  function finishReveal() {
    clearTimers();
    revealPhase.value = "done";
    revealData.value = null;
  }

  function skipReveal() {
    finishReveal();
  }

  function advanceStep(steps: RevealPhase[], index: number) {
    if (index >= steps.length) {
      finishReveal();
      return;
    }
    const phase = steps[index];
    revealPhase.value = phase;
    if (revealData.value) {
      revealData.value = {
        ...revealData.value,
        stepIndex: index + 1,
      };
    }
    if (phase === "dice") {
      diceTimer = setTimeout(() => {
        advanceStep(steps, index + 1);
      }, DICE_DURATION_MS);
      return;
    }
    stepTimer = setTimeout(() => {
      advanceStep(steps, index + 1);
    }, STEP_DURATION_MS);
  }

  function startReveal(result: TurnResult) {
    if (result.dice < 1) return;
    const fingerprint = turnResultFingerprint(result);
    if (seenKeys.has(fingerprint)) return;

    seenKeys.add(fingerprint);
    persistSeenKeys(seenKeys);

    clearTimers();
    const steps = buildSteps(result);
    revealData.value = buildRevealData(result);
    revealPhase.value = "idle";
    advanceStep(steps, 0);
  }

  const isRevealing = computed(
    () =>
      revealPhase.value !== "idle" && revealPhase.value !== "done"
  );

  const hasMessages = computed(() => {
    const msgs =
      lastTurnResult.value?.messages ?? gameState.value?.lastResult?.messages;
    return !!msgs?.length;
  });

  const showLog = computed(() => !isRevealing.value && hasMessages.value);

  watch(
    lastTurnResult,
    (result) => {
      if (result) startReveal(result);
    },
    { immediate: true }
  );

  onUnmounted(() => {
    clearTimers();
  });

  return {
    revealPhase,
    revealData,
    isRevealing,
    showLog,
    hasMessages,
    skipReveal,
  };
}
