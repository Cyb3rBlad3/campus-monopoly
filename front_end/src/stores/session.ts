import { defineStore } from "pinia";
import { ref } from "vue";

const STORAGE_KEY = "campus_monopoly_session";

interface SessionSnapshot {
  roomId: string;
  gameId: string;
  localPlayerId: string;
  playerName: string;
}

/** 房间与本地会话 */
export const useSessionStore = defineStore("session", () => {
  const roomId = ref("");
  const gameId = ref("");
  const localPlayerId = ref("");
  const playerName = ref("玩家");

  function persist() {
    const data: SessionSnapshot = {
      roomId: roomId.value,
      gameId: gameId.value,
      localPlayerId: localPlayerId.value,
      playerName: playerName.value,
    };
    try {
      uni.setStorageSync(STORAGE_KEY, JSON.stringify(data));
    } catch {
      /* ignore */
    }
  }

  function restore() {
    try {
      const raw = uni.getStorageSync(STORAGE_KEY);
      if (!raw) return;
      const data = JSON.parse(String(raw)) as SessionSnapshot;
      roomId.value = data.roomId ?? "";
      gameId.value = data.gameId ?? "";
      localPlayerId.value = data.localPlayerId ?? "";
      playerName.value = data.playerName ?? "玩家";
    } catch {
      /* ignore */
    }
  }

  function setRoom(id: string) {
    roomId.value = id;
    persist();
  }

  function setGame(id: string) {
    gameId.value = id;
    persist();
  }

  function setLocalPlayer(id: string) {
    localPlayerId.value = id;
    persist();
  }

  function setPlayerName(name: string) {
    playerName.value = name;
    persist();
  }

  function clear() {
    roomId.value = "";
    gameId.value = "";
    localPlayerId.value = "";
    try {
      uni.removeStorageSync(STORAGE_KEY);
    } catch {
      /* ignore */
    }
  }

  restore();

  return {
    roomId,
    gameId,
    localPlayerId,
    playerName,
    setRoom,
    setGame,
    setLocalPlayer,
    setPlayerName,
    clear,
    persist,
    restore,
  };
});
