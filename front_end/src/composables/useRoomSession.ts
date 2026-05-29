import { useSessionStore } from "../stores/session";
import { useGameStore } from "../stores/game";
import { useNetworkStore } from "../stores/network";
import { joinRoom, rejoinRoom, touchPresence } from "../api/game";
import {
  assertLocalDeviceCanUseName,
  clearRoomBinding,
  setRoomBinding,
  withDeviceId,
} from "../utils/deviceId";
import {
  isNameTakenInRoom,
  isSamePlayerName,
  normalizePlayerName,
  findPlayerIdByName,
} from "../utils/playerName";
import type { GameState } from "../types/game";
import type { RoomSummary } from "../types/room";
import type { GameMutationResponse } from "../api/http";

export function useRoomSession() {
  const session = useSessionStore();
  const game = useGameStore();
  const network = useNetworkStore();

  function applyGameState(state: GameState, playerId?: string, playerName?: string) {
    session.setRoom(state.roomId);
    session.setGame(state.gameId);
    game.setFromResponse(state, null);
    const pid = playerId ?? session.localPlayerId;
    const pname =
      playerName ??
      state.players.find((p) => p.id === pid)?.name ??
      session.playerName;
    if (pid) session.setLocalPlayer(pid);
    if (pname) session.setPlayerName(pname);
    if (state.roomId && pid && pname) {
      setRoomBinding(state.roomId, { playerId: pid, playerName: pname });
    }
  }

  function validateNameForJoin(
    name: string,
    playerNames: string[]
  ): string | null {
    const normalized = normalizePlayerName(name);
    if (!normalized) return "请输入昵称";
    if (isNameTakenInRoom(playerNames, normalized)) {
      return "该房间已有同名玩家";
    }
    return null;
  }

  async function reconnectToRoom(
    roomId: string,
    name?: string,
    silent = false
  ): Promise<boolean> {
    const playerName = normalizePlayerName(name ?? session.playerName);
    if (!roomId || !playerName) return false;
    if (!network.assertOnline()) return false;

    const res = await rejoinRoom(roomId, withDeviceId({ name: playerName }));
    if (!res.ok) {
      if (res.statusCode === 404) handleRemovedFromRoom(roomId);
      return false;
    }

    applyGameState(res.data.gameState, res.data.playerId, playerName);
    if (!silent) {
      uni.showToast({ title: "已恢复会话", icon: "success" });
    }
    return true;
  }

  async function joinRoomByName(
    roomId: string,
    name: string,
    extra?: Record<string, unknown>
  ): Promise<boolean> {
    const normalized = normalizePlayerName(name);
    if (!normalized) {
      uni.showToast({ title: "请输入昵称", icon: "none" });
      return false;
    }
    if (!network.assertOnline()) return false;

    const localErr = assertLocalDeviceCanUseName(roomId, normalized);
    if (localErr) {
      uni.showToast({ title: localErr, icon: "none" });
      return false;
    }

    const res = await joinRoom(roomId, withDeviceId({ name: normalized, ...extra }));
    if (!res.ok) {
      uni.showToast({ title: res.message, icon: "none" });
      return false;
    }

    const payload = res.data as GameMutationResponse;
    const selfId =
      findPlayerIdByName(payload.gameState.players, normalized) ??
      payload.gameState.players[payload.gameState.players.length - 1]?.id;
    applyGameState(payload.gameState, selfId, normalized);
    return true;
  }

  /** 从房间列表或大厅进入：同名则重连，否则加入（仅 waiting） */
  async function enterRoom(summary: RoomSummary, name: string): Promise<boolean> {
    const normalized = normalizePlayerName(name);
    if (!normalized) {
      uni.showToast({ title: "请输入昵称", icon: "none" });
      return false;
    }
    if (!network.assertOnline()) return false;

    const hasNickname = summary.playerNames.some((n) =>
      isSamePlayerName(n, normalized)
    );

    if (hasNickname) {
      return reconnectToRoom(summary.roomId, normalized);
    }

    if (summary.status !== "waiting") {
      uni.showToast({
        title: "对局已开始，仅支持用原昵称重连",
        icon: "none",
      });
      return false;
    }

    if (summary.playerCount >= summary.maxPlayers) {
      uni.showToast({ title: "房间人数已满", icon: "none" });
      return false;
    }

    const err = validateNameForJoin(normalized, summary.playerNames);
    if (err) {
      uni.showToast({ title: err, icon: "none" });
      return false;
    }

    const localErr = assertLocalDeviceCanUseName(summary.roomId, normalized);
    if (localErr) {
      uni.showToast({ title: localErr, icon: "none" });
      return false;
    }

    const ok = await joinRoomByName(summary.roomId, normalized);
    if (ok) uni.showToast({ title: "已加入房间", icon: "success" });
    return ok;
  }

  /** 断线恢复：优先用本地 roomId + 昵称重连 */
  async function tryAutoReconnect(): Promise<boolean> {
    if (!session.roomId || !session.playerName) return false;
    if (!network.isOnline) return false;
    return reconnectToRoom(session.roomId, session.playerName, true);
  }

  function handleRemovedFromRoom(roomId?: string, navigateHome = false) {
    const rid = roomId ?? session.roomId;
    if (rid) clearRoomBinding(rid);
    session.clear();
    game.clear();
    uni.showToast({
      title: "已超过 60 秒未恢复，已被移出房间",
      icon: "none",
      duration: 3000,
    });
    if (navigateHome) {
      uni.reLaunch({ url: "/pages/index/index" });
    }
  }

  /** 心跳：保持在线，避免 60 秒被踢 */
  async function pingPresence(roomId?: string): Promise<boolean> {
    const rid = roomId ?? session.roomId;
    const name = normalizePlayerName(session.playerName);
    if (!rid || !name || !network.isOnline) return false;

    const res = await touchPresence(rid, withDeviceId({ name }));
    if (res.ok) return true;

    if (res.statusCode === 404) {
      handleRemovedFromRoom(rid, true);
      return false;
    }
    return false;
  }

  return {
    applyGameState,
    validateNameForJoin,
    joinRoomByName,
    reconnectToRoom,
    enterRoom,
    tryAutoReconnect,
    pingPresence,
    handleRemovedFromRoom,
  };
}
