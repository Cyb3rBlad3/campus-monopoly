import { defineStore } from "pinia";
import { ref } from "vue";

/** 房间与本地会话（具体字段与后端协商后可扩展） */
export const useSessionStore = defineStore("session", () => {
  const roomId = ref("");
  const gameId = ref("");
  const localPlayerId = ref("");

  function setRoom(id: string) {
    roomId.value = id;
  }

  function setGame(id: string) {
    gameId.value = id;
  }

  function setLocalPlayer(id: string) {
    localPlayerId.value = id;
  }

  function clear() {
    roomId.value = "";
    gameId.value = "";
    localPlayerId.value = "";
  }

  return {
    roomId,
    gameId,
    localPlayerId,
    setRoom,
    setGame,
    setLocalPlayer,
    clear,
  };
});
