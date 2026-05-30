<template>
  <view class="page">
    <OfflineBanner />

    <view class="hero">
      <text class="title">CampusMonopoly</text>
      <text class="subtitle">校园版大富翁 · H5</text>
    </view>

    <view class="section">
      <text class="label">你的昵称</text>
      <input
        :value="playerNameInput"
        class="input"
        type="text"
        maxlength="32"
        placeholder="打开后自动分配校园昵称"
        @input="onPlayerNameInput"
      />
    </view>

    <view class="section">
      <view class="section-head">
        <text class="section-title">可加入的房间</text>
        <button class="btn-mini" :disabled="listLoading" @click="loadRoomList">
          刷新
        </button>
      </view>
      <text v-if="listError" class="err">{{ listError }}</text>
      <view v-if="!listLoading && rooms.length === 0" class="empty-list">
        <text>暂无等待中的房间，可点击下方创建。</text>
      </view>
      <view
        v-for="room in rooms"
        :key="room.roomId"
        class="room-card"
        @click="onJoinRoom(room)"
      >
        <view class="room-head">
          <text class="room-id">{{ room.roomId }}</text>
          <text class="room-status">{{ roomStatusLabel(room) }}</text>
        </view>
        <text class="room-meta">
          {{ room.playerCount }}/{{ room.maxPlayers }} 人 · 生活费 ¥{{ room.initialAllowance }}
        </text>
        <text v-if="room.playerNames.length" class="room-players">
          玩家：{{ room.playerNames.join("、") }}
        </text>
        <text v-if="roomExpiryHint(room)" class="room-expire">{{ roomExpiryHint(room) }}</text>
        <text class="room-action">{{ roomActionHint(room) }}</text>
      </view>
    </view>

    <view class="actions">
      <button class="btn primary" @click="goCreate">创建新房间</button>
      <button
        v-if="session.gameId"
        class="btn"
        :disabled="!network.isOnline"
        @click="goBoard"
      >
        继续对局
      </button>
    </view>

    <view class="tips">
      <text class="tip-line">接口：{{ apiBase || "未配置 VITE_API_BASE_URL" }}</text>
      <text class="tip-line">超过 60 秒未恢复连接将被踢出房间；等待房 15 分钟无活动自动关闭。</text>
      <text class="tip-line">断线恢复网络后将按本地昵称自动重连。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useSessionStore } from "../../stores/session";
import { useGameStore } from "../../stores/game";
import { useNetworkStore } from "../../stores/network";
import { useRoomSession } from "../../composables/useRoomSession";
import { listRooms } from "../../api/game";
import { getApiBaseUrl } from "../../config/env";
import { isSamePlayerName, normalizePlayerName } from "../../utils/playerName";
import {
  collectOnlinePlayerNames,
  pickRandomDictionaryName,
  suggestDictionaryPlayerName,
} from "../../utils/playerNameDictionary";
import { getDeviceId, getRoomBinding } from "../../utils/deviceId";
import type { RoomSummary } from "../../types/room";

const session = useSessionStore();
const game = useGameStore();
const network = useNetworkStore();
const { enterRoom, tryAutoReconnect } = useRoomSession();

const playerNameInput = ref("");
const rooms = ref<RoomSummary[]>([]);
const listLoading = ref(false);
const listError = ref("");
const joiningRoomId = ref("");
const nameManuallyEdited = ref(false);

const apiBase = computed(() => getApiBaseUrl());

function readInputValue(e: Event | { detail?: { value?: string } }): string {
  const uniEvent = e as { detail?: { value?: string } };
  const detail = uniEvent.detail?.value;
  if (detail !== undefined) return detail;
  const domEvent = e as Event;
  return (domEvent.target as HTMLInputElement | null)?.value ?? "";
}

function onPlayerNameInput(e: Event) {
  nameManuallyEdited.value = true;
  playerNameInput.value = readInputValue(e);
  session.setPlayerName(normalizePlayerName(playerNameInput.value) || "玩家");
}

function applySuggestedPlayerName(usedNames: string[], preferredName?: string) {
  const binding = session.roomId ? getRoomBinding(session.roomId) : null;
  if (binding?.playerName) {
    playerNameInput.value = binding.playerName;
    session.setPlayerName(binding.playerName);
    nameManuallyEdited.value = true;
    return;
  }
  if (nameManuallyEdited.value) {
    const current = normalizePlayerName(playerNameInput.value);
    if (current && !usedNames.some((n) => isSamePlayerName(n, current))) {
      session.setPlayerName(current);
      return;
    }
  }
  const picked = suggestDictionaryPlayerName(usedNames, {
    preferredName: preferredName ?? session.playerName,
    selfName: binding?.playerName,
  });
  playerNameInput.value = picked;
  session.setPlayerName(picked);
}

function roomStatusLabel(room: RoomSummary): string {
  if (room.status === "waiting") return "等待中";
  if (room.status === "playing") return "进行中";
  if (room.status === "finished") return "已结束";
  return room.status;
}

function roomExpiryHint(room: RoomSummary): string {
  if (room.status !== "waiting" || !room.expiresAt) return "";
  const left = Math.max(
    0,
    Math.ceil((new Date(room.expiresAt).getTime() - Date.now()) / 1000)
  );
  if (left <= 120) return "即将关闭";
  const minutes = Math.ceil(left / 60);
  return `约 ${minutes} 分钟无活动后自动关闭`;
}

function roomActionHint(room: RoomSummary): string {
  const name = normalizePlayerName(playerNameInput.value);
  if (name && room.playerNames.some((n) => isSamePlayerName(n, name))) {
    return "点击恢复连接";
  }
  if (room.status === "waiting" && room.playerCount < room.maxPlayers) {
    return "点击加入";
  }
  if (room.status === "playing") {
    return "仅支持原昵称重连";
  }
  return "已满或不可加入";
}

async function loadRoomList() {
  if (!network.assertOnline()) return;
  listLoading.value = true;
  listError.value = "";
  const res = await listRooms({ limit: 30 });
  listLoading.value = false;
  if (!res.ok) {
    listError.value = res.message;
    return;
  }
  rooms.value = res.data.filter((r) => r.status !== "finished");
  applySuggestedPlayerName(collectOnlinePlayerNames(rooms.value));
}

async function onJoinRoom(room: RoomSummary) {
  if (joiningRoomId.value) return;
  let name = normalizePlayerName(playerNameInput.value);
  if (!name) {
    name = pickRandomDictionaryName(room.playerNames);
    playerNameInput.value = name;
    session.setPlayerName(name);
  }
  joiningRoomId.value = room.roomId;
  try {
    const ok = await enterRoom(room, name);
    if (!ok) return;
    if (room.status === "playing" || game.gameState?.status === "playing") {
      uni.navigateTo({ url: "/pages/game/board" });
    } else {
      uni.navigateTo({ url: "/pages/room/create" });
    }
  } finally {
    joiningRoomId.value = "";
  }
}

function goCreate() {
  uni.navigateTo({ url: "/pages/room/create" });
}

async function goBoard() {
  if (!network.assertOnline()) return;
  if (session.roomId && session.playerName) {
    await tryAutoReconnect();
  } else if (session.gameId) {
    await game.refresh(session.gameId);
  }
  uni.navigateTo({ url: "/pages/game/board" });
}

onMounted(() => {
  network.init();
  getDeviceId();
  applySuggestedPlayerName([], session.playerName);
  loadRoomList();
});

onShow(() => {
  if (network.isOnline) {
    tryAutoReconnect();
    loadRoomList();
  }
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx 40rpx 48rpx;
  box-sizing: border-box;
  background: linear-gradient(180deg, #e8f5e9 0%, #f5faf6 40%);
}
.hero {
  margin: 24rpx 0 32rpx;
}
.title {
  display: block;
  font-size: 52rpx;
  font-weight: 700;
  color: #1b5e20;
}
.subtitle {
  display: block;
  margin-top: 12rpx;
  font-size: 28rpx;
  color: #558b2f;
}
.section {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1px solid #e0e0e0;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1b5e20;
}
.label {
  display: block;
  font-size: 26rpx;
  color: #424242;
  margin-bottom: 12rpx;
}
.input {
  width: 100%;
  min-height: 72rpx;
  padding: 20rpx 24rpx;
  border: 1px solid #c8e6c9;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
  background: #fff;
}
.btn-mini {
  font-size: 24rpx;
  padding: 8rpx 20rpx;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 8rpx;
}
.room-card {
  padding: 20rpx;
  margin-bottom: 16rpx;
  border-radius: 12rpx;
  border: 1px solid #c8e6c9;
  background: #f9fdfb;
}
.room-card:active {
  background: #e8f5e9;
}
.room-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.room-id {
  font-size: 26rpx;
  font-weight: 700;
  color: #212121;
}
.room-status {
  font-size: 22rpx;
  color: #558b2f;
}
.room-meta,
.room-players {
  display: block;
  font-size: 24rpx;
  color: #616161;
  margin-top: 8rpx;
}
.room-expire {
  display: block;
  font-size: 22rpx;
  color: #ef6c00;
  margin-top: 6rpx;
}
.room-action {
  display: block;
  font-size: 22rpx;
  color: #2e7d32;
  margin-top: 8rpx;
}
.empty-list {
  font-size: 26rpx;
  color: #757575;
  padding: 16rpx 0;
}
.err {
  color: #c62828;
  font-size: 24rpx;
  margin-bottom: 12rpx;
  display: block;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.btn {
  border-radius: 16rpx;
}
.btn.primary {
  background-color: #2e7d32;
  color: #fff;
}
.tips {
  margin-top: 32rpx;
  padding: 24rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12rpx;
}
.tip-line {
  display: block;
  font-size: 24rpx;
  color: #616161;
  line-height: 1.6;
  margin-bottom: 8rpx;
}
</style>
