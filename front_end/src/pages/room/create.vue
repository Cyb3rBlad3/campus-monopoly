<template>
  <view class="page">
    <OfflineBanner />

    <view class="section">
      <text class="section-title">玩家设置</text>
      <view class="field">
        <text class="label">昵称</text>
        <input
          :value="playerNameInput"
          class="input"
          type="text"
          maxlength="32"
          placeholder="2-4 人本地轮流游玩"
          @input="onPlayerNameInput"
        />
      </view>
      <view class="field">
        <text class="label">每月生活费</text>
        <picker
          mode="selector"
          :range="allowanceLabels"
          :value="allowanceIndex"
          @change="onAllowanceChange"
        >
          <view class="picker-value">{{ allowanceLabels[allowanceIndex] }}</view>
        </picker>
      </view>
      <view class="field">
        <text class="label">储蓄目标</text>
        <picker
          mode="selector"
          :range="goalLabels"
          :value="goalIndex"
          @change="onGoalChange"
        >
          <view class="picker-value">{{ goalLabels[goalIndex] }}</view>
        </picker>
      </view>
    </view>

    <view class="section">
      <text class="section-title">房间</text>
      <view class="field">
        <text class="label">房间号（加入他人房间时填写）</text>
        <input
          :value="roomIdInput"
          class="input"
          type="text"
          maxlength="64"
          placeholder="创建后自动填入"
          @input="onRoomIdInput"
        />
      </view>
      <button class="btn primary" :disabled="loading" @click="handleCreateRoom">
        创建宿舍房间
      </button>
      <button class="btn secondary" :disabled="loading" @click="handleJoinRoom">
        加入房间
      </button>
      <button class="btn ghost" :disabled="loading || !roomIdInput" @click="refreshLobby">
        刷新玩家列表
      </button>
    </view>

    <view v-if="game.gameState" class="section lobby">
      <text class="section-title">等待大厅</text>
      <text class="meta">状态：{{ statusLabel }}</text>
      <text class="meta">房间 {{ game.gameState.roomId }}</text>
      <text class="meta">玩家 {{ game.gameState.players.length }} / {{ game.gameState.settings.maxPlayers }}</text>
      <view
        v-for="p in game.gameState.players"
        :key="p.id"
        class="player-row"
        :class="{ me: p.id === session.localPlayerId }"
      >
        <text class="player-name">{{ p.name }}</text>
        <text v-if="p.id === session.localPlayerId" class="tag">我</text>
        <text v-if="p.bankrupt" class="tag warn">破产</text>
      </view>
      <button
        v-if="canStart"
        class="btn primary"
        :disabled="loading"
        @click="handleStartGame"
      >
        开始游戏（至少 2 人）
      </button>
      <button
        v-if="game.gameState.status === 'playing'"
        class="btn primary"
        @click="goBoard"
      >
        进入棋盘
      </button>
    </view>

    <view class="note">
      <text>本机同一房间只能使用一个昵称；超过 60 秒未恢复将被踢出；等待房 1 分钟无活动自动关闭。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useSessionStore } from "../../stores/session";
import { useGameStore } from "../../stores/game";
import { useNetworkStore } from "../../stores/network";
import { useRoomSession } from "../../composables/useRoomSession";
import { createRoom, joinRoom } from "../../api/game";
import type { GameMutationResponse } from "../../api/http";
import {
  findPlayerIdByName,
  normalizePlayerName,
} from "../../utils/playerName";
import {
  assertLocalDeviceCanUseName,
  getDeviceId,
  getRoomBinding,
  withDeviceId,
} from "../../utils/deviceId";
import {
  ALLOWANCE_OPTIONS,
  SAVING_GOAL_OPTIONS,
} from "../../utils/gameLabels";
import type { GameState } from "../../types/game";

const session = useSessionStore();
const game = useGameStore();
const network = useNetworkStore();
const {
  applyGameState,
  joinRoomByName,
  tryAutoReconnect,
  reconnectToRoom,
  pingPresence,
} = useRoomSession();

const PRESENCE_INTERVAL_MS = 20_000;
let presenceTimer: ReturnType<typeof setInterval> | null = null;

function startPresenceHeartbeat() {
  stopPresenceHeartbeat();
  presenceTimer = setInterval(() => {
    if (session.roomId && game.gameState?.status === "waiting") {
      pingPresence();
    }
  }, PRESENCE_INTERVAL_MS);
}

function stopPresenceHeartbeat() {
  if (presenceTimer) {
    clearInterval(presenceTimer);
    presenceTimer = null;
  }
}

const roomIdInput = ref("");
const playerNameInput = ref("玩家");
const loading = ref(false);
const allowanceIndex = ref(1);
const goalIndex = ref(1);

const allowanceLabels = ALLOWANCE_OPTIONS.map((o) => o.label);
const goalLabels = SAVING_GOAL_OPTIONS.map((o) => o.label);

const statusLabel = computed(() => {
  const s = game.gameState?.status;
  if (s === "waiting") return "等待中";
  if (s === "playing") return "对局进行中";
  if (s === "finished") return "已结束";
  return s ?? "—";
});

const canStart = computed(() => {
  const gs = game.gameState;
  return (
    !!gs &&
    gs.status === "waiting" &&
    gs.players.length >= 2 &&
    !!session.roomId
  );
});

function readInputValue(e: Event | { detail?: { value?: string } }): string {
  const uniEvent = e as { detail?: { value?: string } };
  const detail = uniEvent.detail?.value;
  if (detail !== undefined) return detail;
  const domEvent = e as Event;
  return (domEvent.target as HTMLInputElement | null)?.value ?? "";
}

function onRoomIdInput(e: Event) {
  roomIdInput.value = readInputValue(e);
}

function onPlayerNameInput(e: Event) {
  playerNameInput.value = readInputValue(e);
  session.setPlayerName(playerNameInput.value.trim() || "玩家");
}

function onAllowanceChange(e: { detail: { value: string } }) {
  allowanceIndex.value = Number(e.detail.value);
}

function onGoalChange(e: { detail: { value: string } }) {
  goalIndex.value = Number(e.detail.value);
}

function syncRoomFields(state: GameState) {
  roomIdInput.value = state.roomId;
  applyGameState(state, session.localPlayerId || undefined);
}

async function handleCreateRoom() {
  if (loading.value || !network.assertOnline()) return;
  loading.value = true;
  try {
    const allowance = ALLOWANCE_OPTIONS[allowanceIndex.value].value;
    const result = await createRoom({
      maxPlayers: 4,
      initialAllowance: allowance,
    });
    if (!result.ok) {
      uni.showToast({ title: result.message, icon: "none" });
      return;
    }
    const data = result.data as GameState;
    syncRoomFields(data);
    const name = normalizePlayerName(playerNameInput.value) || "玩家";
    const savingGoalType = SAVING_GOAL_OPTIONS[goalIndex.value].value;
    const ok = await joinRoomByName(data.roomId, name, {
      savingGoalType,
      pieceColor: "#2e7d32",
    });
    if (ok) uni.showToast({ title: "房间已创建，等待好友加入", icon: "success" });
  } finally {
    loading.value = false;
  }
}

async function handleJoinRoom() {
  const roomId = roomIdInput.value.trim();
  if (!roomId) {
    uni.showToast({ title: "请填写房间号", icon: "none" });
    return;
  }
  if (loading.value || !network.assertOnline()) return;

  const name = normalizePlayerName(playerNameInput.value) || "玩家";
  loading.value = true;
  try {
    const savingGoalType = SAVING_GOAL_OPTIONS[goalIndex.value].value;
    const pieceColor = ["#2e7d32", "#1565c0", "#ef6c00", "#6a1b9a"][
      game.gameState?.players.length ?? 0
    ];
    const localErr = assertLocalDeviceCanUseName(roomId, name);
    if (localErr) {
      uni.showToast({ title: localErr, icon: "none" });
      return;
    }
    const res = await joinRoom(
      roomId,
      withDeviceId({ name, savingGoalType, pieceColor })
    );
    if (res.ok) {
      const payload = res.data as GameMutationResponse;
      const selfId = findPlayerIdByName(payload.gameState.players, name);
      applyGameState(payload.gameState, selfId, name);
      uni.showToast({ title: "已加入房间", icon: "success" });
      return;
    }
    if (res.message.includes("同名")) {
      await reconnectToRoom(roomId, name);
      return;
    }
    uni.showToast({ title: res.message, icon: "none" });
  } finally {
    loading.value = false;
  }
}

async function refreshLobby() {
  if (!session.gameId) {
    uni.showToast({ title: "请先创建或加入房间", icon: "none" });
    return;
  }
  loading.value = true;
  await game.refresh(session.gameId);
  loading.value = false;
}

async function handleStartGame() {
  if (!session.roomId) return;
  loading.value = true;
  const ok = await game.startGame(session.roomId);
  loading.value = false;
  if (ok) {
    uni.showToast({ title: "游戏开始", icon: "success" });
    goBoard();
  }
}

function goBoard() {
  if (!session.gameId) {
    uni.showToast({ title: "缺少 gameId", icon: "none" });
    return;
  }
  uni.navigateTo({ url: "/pages/game/board" });
}

onMounted(async () => {
  network.init();
  getDeviceId();
  const binding = session.roomId ? getRoomBinding(session.roomId) : null;
  playerNameInput.value =
    binding?.playerName || session.playerName || "玩家";
  roomIdInput.value = session.roomId;
  if (session.gameId) {
    await game.refresh(session.gameId);
  } else if (session.roomId) {
    await tryAutoReconnect();
  }
  startPresenceHeartbeat();
});

onShow(() => {
  if (network.isOnline) {
    tryAutoReconnect().then(() => pingPresence());
  }
});

onUnmounted(() => {
  stopPresenceHeartbeat();
});
</script>

<style scoped>
.page {
  padding: 32rpx;
  min-height: 100vh;
  box-sizing: border-box;
  background: #f5faf6;
}
.section {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 28rpx;
  border: 1px solid #e0e0e0;
}
.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1b5e20;
  margin-bottom: 20rpx;
}
.field {
  margin-bottom: 24rpx;
}
.label {
  display: block;
  font-size: 26rpx;
  color: #424242;
  margin-bottom: 12rpx;
}
.input,
.picker-value {
  width: 100%;
  min-height: 72rpx;
  padding: 20rpx 24rpx;
  border: 1px solid #c8e6c9;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
  background: #fff;
}
.picker-value {
  line-height: 72rpx;
  color: #212121;
}
.btn {
  margin-top: 20rpx;
  border-radius: 12rpx;
}
.btn.primary {
  background-color: #2e7d32;
  color: #fff;
}
.btn.secondary {
  background-color: #558b2f;
  color: #fff;
}
.btn.ghost {
  background: #fff;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}
.lobby .meta {
  display: block;
  font-size: 26rpx;
  color: #616161;
  margin-bottom: 8rpx;
}
.player-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 0;
  border-bottom: 1px solid #eeeeee;
}
.player-row.me {
  background: #e8f5e9;
  margin: 0 -16rpx;
  padding-left: 16rpx;
  padding-right: 16rpx;
  border-radius: 8rpx;
}
.player-name {
  font-size: 28rpx;
  color: #212121;
}
.tag {
  font-size: 22rpx;
  color: #2e7d32;
  background: #c8e6c9;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.tag.warn {
  color: #c62828;
  background: #ffcdd2;
}
.note {
  font-size: 24rpx;
  color: #757575;
  line-height: 1.6;
}
</style>
