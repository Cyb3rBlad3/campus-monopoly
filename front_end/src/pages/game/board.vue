<template>
  <view class="page">
    <view class="card">
      <text class="label">当前 gameId</text>
      <text class="value">{{ session.gameId || "未设置" }}</text>
    </view>
    <view class="card">
      <text class="label">房间 roomId</text>
      <text class="value">{{ session.roomId || "未设置" }}</text>
    </view>
    <button
      class="btn primary"
      :loading="game.loading"
      :disabled="!session.gameId"
      @click="refresh"
    >
      拉取 GameState
    </button>
    <view v-if="game.errorMessage" class="err">{{ game.errorMessage }}</view>
    <view v-if="game.gameState" class="card state">
      <text class="label">状态</text>
      <text class="mono">status: {{ game.gameState.status }}</text>
      <text class="mono">round: {{ game.gameState.round }}</text>
      <text class="mono">current: {{ game.gameState.currentPlayerId }}</text>
      <text class="mono">players: {{ game.gameState.players.length }}</text>
    </view>
    <view v-if="game.lastTurnResult?.messages?.length" class="card">
      <text class="label">上次 TurnResult 摘要</text>
      <text
        v-for="(m, i) in game.lastTurnResult.messages"
        :key="i"
        class="mono"
      >{{ m }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { useSessionStore } from "../../stores/session";
import { useGameStore } from "../../stores/game";
import { getGame } from "../../api/game";
import type { GameState } from "../../types/game";

const session = useSessionStore();
const game = useGameStore();

async function refresh() {
  if (!session.gameId) return;
  game.loading = true;
  game.errorMessage = "";
  const res = await getGame(session.gameId);
  game.loading = false;
  if (res.ok) {
    game.setFromResponse(res.data as GameState, null);
  } else {
    game.errorMessage = res.message;
  }
}
</script>

<style scoped>
.page {
  padding: 32rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
.card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1px solid #e0e0e0;
}
.label {
  display: block;
  font-size: 24rpx;
  color: #757575;
  margin-bottom: 8rpx;
}
.value {
  font-size: 30rpx;
  color: #212121;
  word-break: break-all;
}
.mono {
  display: block;
  font-size: 24rpx;
  color: #424242;
  font-family: ui-monospace, monospace;
  margin-top: 6rpx;
}
.btn {
  margin-bottom: 24rpx;
  border-radius: 12rpx;
}
.btn.primary {
  background-color: #2e7d32;
  color: #fff;
}
.err {
  color: #c62828;
  font-size: 26rpx;
  margin-bottom: 16rpx;
}
.state .mono {
  margin-top: 12rpx;
}
</style>
