<template>
  <view class="page">
    <OfflineBanner />

    <view v-if="!gameState" class="empty">
      <text>未加载对局，请从房间页进入。</text>
      <button class="btn" @click="goRoom">返回房间</button>
    </view>

    <template v-else>
      <view class="top-bar">
        <text class="round">第 {{ gameState.round }} 回合</text>
        <text class="phase">{{ phaseLabel }}</text>
        <button class="btn-mini" :loading="game.loading" @click="onRefresh">刷新</button>
      </view>

      <image
        class="board-img"
        src="/static/board/campus_board_v2.svg"
        mode="widthFix"
      />

      <scroll-view scroll-x class="tile-strip">
        <view
          v-for="tile in sortedBoard"
          :key="tile.id"
          class="tile-chip"
          :class="{
            current: currentTile?.id === tile.id,
            landed: playersOnTile(tile.position).length > 0,
          }"
        >
          <image
            v-if="tile.icon"
            class="tile-icon"
            :src="tileIconPath(tile.icon)"
            mode="aspectFit"
          />
          <text class="tile-name">{{ tile.name }}</text>
          <text v-if="tile.cost > 0" class="tile-cost">¥{{ tile.cost }}</text>
          <view class="pieces">
            <view
              v-for="p in playersOnTile(tile.position)"
              :key="p.id"
              class="piece-dot"
              :style="{ background: p.pieceColor || '#2e7d32' }"
            />
          </view>
        </view>
      </scroll-view>

      <view class="players-panel">
        <view
          v-for="p in gameState.players"
          :key="p.id"
          class="player-card"
          :class="{
            current: p.id === gameState.currentPlayerId,
            me: p.id === session.localPlayerId,
            bankrupt: p.bankrupt,
          }"
        >
          <text class="p-name">{{ p.name }}</text>
          <text v-if="p.id === session.localPlayerId" class="badge">我</text>
          <text v-if="p.id === gameState.currentPlayerId" class="badge turn">回合</text>
          <text class="stat">¥{{ p.money }} · 格{{ p.position + 1 }}</text>
          <text class="stat sub">社交{{ p.socialValue }} 理财{{ p.financeValue }}</text>
          <text class="stat sub">心情{{ p.mood }} 精力{{ p.energy }} 成绩{{ p.grade }}</text>
          <text v-if="p.handCards?.length" class="stat sub">手牌 {{ p.handCards.length }} 张</text>
        </view>
      </view>

      <view v-if="lastMessages.length" class="log-card">
        <text class="log-title">本回合动态</text>
        <text v-for="(m, i) in lastMessages" :key="i" class="log-line">{{ m }}</text>
      </view>

      <view v-if="gameState.status === 'playing'" class="actions">
        <text class="actions-title">
          {{ isMyTurn ? "你的回合" : `等待 ${currentPlayer?.name ?? "其他玩家"}` }}
        </text>

        <button
          v-if="canRoll"
          class="btn primary"
          :disabled="game.loading"
          @click="onRoll"
        >
          投掷骰子
        </button>

        <view v-if="canTileAction && currentTile?.actions?.length" class="action-group">
          <text class="group-label">地块行动（{{ currentTile.name }}）</text>
          <button
            v-for="act in currentTile.actions"
            :key="act"
            class="btn secondary"
            :disabled="game.loading"
            @click="onTileAction(act)"
          >
            {{ tileActionLabel(act) }}
          </button>
        </view>

        <view v-if="canUseCard && playableCards.length" class="action-group">
          <text class="group-label">使用行动牌（每回合 1 张）</text>
          <button
            v-for="card in playableCards"
            :key="card.id"
            class="btn secondary"
            :disabled="game.loading"
            @click="onUseCard(card.id)"
          >
            {{ card.name }}
          </button>
        </view>

        <button
          v-if="canEndTurn"
          class="btn ghost"
          :disabled="game.loading"
          @click="onEndTurn"
        >
          结束回合
        </button>

        <text v-if="isMyTurn && localPlayer?.turnFlags?.rolled" class="hint">
          流程：已掷骰后可执行地块行动、使用行动牌，最后结束回合。
        </text>
      </view>

      <view v-if="gameState.status === 'finished'" class="result-card">
        <text class="result-title">对局结束</text>
        <text class="result-winner">
          获胜：{{ winnerName }}
        </text>
        <button class="btn primary" @click="goRoom">返回房间</button>
      </view>
    </template>

    <view v-if="game.errorMessage" class="err">{{ game.errorMessage }}</view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useSessionStore } from "../../stores/session";
import { useGameStore } from "../../stores/game";
import { useNetworkStore } from "../../stores/network";
import { useGamePlay } from "../../composables/useGamePlay";
import { useRoomSession } from "../../composables/useRoomSession";
import {
  TILE_ACTION_LABELS,
  tileIconPath,
} from "../../utils/gameLabels";
import type { Player } from "../../types/game";

const session = useSessionStore();
const game = useGameStore();
const network = useNetworkStore();
const { tryAutoReconnect, pingPresence } = useRoomSession();
const {
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
} = useGamePlay();

let pollTimer: ReturnType<typeof setInterval> | null = null;
let presenceTimer: ReturnType<typeof setInterval> | null = null;
const PRESENCE_INTERVAL_MS = 20_000;

const sortedBoard = computed(() => {
  const gs = gameState.value;
  if (!gs) return [];
  return [...gs.board].sort((a, b) => a.position - b.position);
});

const phaseLabel = computed(() => {
  const gs = gameState.value;
  if (!gs) return "";
  if (gs.status === "waiting") return "等待开局";
  if (gs.status === "finished") return "已结束";
  if (gs.turnPhase === "awaiting_roll") return "请掷骰";
  if (gs.turnPhase === "awaiting_action") return "请选择行动";
  return gs.turnPhase ?? "";
});

const lastMessages = computed(() => {
  const msgs = game.lastTurnResult?.messages ?? gameState.value?.lastResult?.messages;
  return msgs?.length ? msgs : [];
});

const winnerName = computed(() => {
  const gs = gameState.value;
  if (!gs?.winnerPlayerId) return "—";
  return gs.players.find((p) => p.id === gs.winnerPlayerId)?.name ?? "—";
});

function playersOnTile(position: number): Player[] {
  const gs = gameState.value;
  if (!gs) return [];
  return gs.players.filter((p) => !p.bankrupt && p.position === position);
}

function tileActionLabel(action: string): string {
  return TILE_ACTION_LABELS[action] ?? action;
}

function goRoom() {
  uni.navigateTo({ url: "/pages/room/create" });
}

async function onRefresh() {
  if (!session.gameId || !network.assertOnline()) return;
  await game.refresh(session.gameId);
}

async function onRoll() {
  if (!session.gameId || !session.localPlayerId || !network.assertOnline()) return;
  await game.roll(session.gameId, session.localPlayerId);
}

async function onTileAction(action: string) {
  if (!session.gameId || !session.localPlayerId || !network.assertOnline()) return;
  if (action === "social_interaction") {
    if (!otherPlayers.value.length) {
      uni.showToast({ title: "没有其他玩家可互动", icon: "none" });
      return;
    }
    const names = otherPlayers.value.map((p) => p.name);
    uni.showActionSheet({
      itemList: names,
      success: async (res) => {
        const target = otherPlayers.value[res.tapIndex];
        if (target) {
          await game.doTileAction(session.gameId, session.localPlayerId, action, {
            targetPlayerId: target.id,
          });
        }
      },
    });
    return;
  }
  if (action === "deposit") {
    uni.showModal({
      title: "定期存款",
      editable: true,
      placeholderText: "200",
      content: "输入存入金额（3 回合后返还本金+10%利息）",
      success: async (res) => {
        if (!res.confirm) return;
        const amount = parseInt(String(res.content || "200"), 10) || 200;
        await game.doTileAction(session.gameId, session.localPlayerId, action, {
          amount,
        });
      },
    });
    return;
  }
  await game.doTileAction(session.gameId, session.localPlayerId, action);
}

async function onUseCard(cardId: string) {
  if (!session.gameId || !session.localPlayerId || !network.assertOnline()) return;
  await game.playCard(session.gameId, session.localPlayerId, cardId);
}

async function onEndTurn() {
  if (!session.gameId || !session.localPlayerId || !network.assertOnline()) return;
  await game.finishTurn(session.gameId, session.localPlayerId);
}

onMounted(async () => {
  network.init();
  if (!session.gameId && session.roomId) {
    await tryAutoReconnect();
  }
  if (!session.gameId) {
    uni.showToast({ title: "请先加入房间", icon: "none" });
    return;
  }
  if (network.isOnline) {
    await game.refresh(session.gameId);
  }
  pollTimer = setInterval(() => {
    const gs = game.gameState;
    if (
      network.isOnline &&
      gs?.status === "playing" &&
      gs.currentPlayerId !== session.localPlayerId &&
      !game.loading
    ) {
      game.refresh(session.gameId);
    }
  }, 4000);

  presenceTimer = setInterval(() => {
    if (session.roomId) pingPresence();
  }, PRESENCE_INTERVAL_MS);
});

onShow(async () => {
  if (network.isOnline) {
    await tryAutoReconnect();
    await pingPresence();
    if (session.gameId) {
      await game.refresh(session.gameId);
    }
  }
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  if (presenceTimer) clearInterval(presenceTimer);
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 16rpx;
  box-sizing: border-box;
  background: #f5faf6;
  overflow: hidden;
}
.empty {
  padding: 48rpx;
  text-align: center;
  color: #616161;
}
.top-bar {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
  margin-bottom: 12rpx;
}
.round {
  font-size: 26rpx;
  font-weight: 700;
  color: #1b5e20;
}
.phase {
  flex: 1;
  font-size: 24rpx;
  color: #558b2f;
}
.btn-mini {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  line-height: 1.4;
  background: #fff;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
  border-radius: 8rpx;
}
.game-main {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 12rpx;
}
.board-column {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.board-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 12rpx;
  overflow: hidden;
}
.board-img {
  width: 100%;
  height: 100%;
}
.tile-strip {
  flex-shrink: 0;
  height: 130rpx;
  margin-top: 10rpx;
  white-space: nowrap;
}
.tile-strip-inner {
  display: inline-flex;
  padding: 4rpx 0;
}
.tile-chip {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 96rpx;
  margin-right: 8rpx;
  padding: 8rpx;
  background: #fff;
  border-radius: 10rpx;
  border: 2px solid #e0e0e0;
  flex-shrink: 0;
}
.tile-chip.current {
  border-color: #2e7d32;
  background: #e8f5e9;
}
.tile-icon {
  width: 40rpx;
  height: 40rpx;
}
.tile-name {
  font-size: 18rpx;
  color: #212121;
  margin-top: 4rpx;
  white-space: normal;
  text-align: center;
  line-height: 1.2;
}
.tile-cost {
  font-size: 16rpx;
  color: #c62828;
}
.pieces {
  display: flex;
  gap: 4rpx;
  margin-top: 4rpx;
  min-height: 12rpx;
  flex-wrap: wrap;
  justify-content: center;
}
.piece-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  border: 1px solid #fff;
}
.players-column {
  width: 220rpx;
  flex-shrink: 0;
  height: 100%;
}
.players-panel {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.player-card {
  background: #fff;
  border-radius: 10rpx;
  padding: 12rpx;
  border: 1px solid #e0e0e0;
}
.player-card.current {
  border-color: #ffb74d;
}
.player-card.me {
  border-left: 4rpx solid #2e7d32;
}
.player-card.bankrupt {
  opacity: 0.5;
}
.p-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 4rpx;
}
.p-name {
  font-size: 24rpx;
  font-weight: 700;
  color: #212121;
  flex: 1;
  line-height: 1.2;
}
.p-badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2rpx;
  flex-shrink: 0;
}
.badge {
  font-size: 18rpx;
  color: #2e7d32;
  line-height: 1.2;
}
.badge.turn {
  color: #ef6c00;
}
.stat {
  display: block;
  font-size: 20rpx;
  color: #424242;
  margin-top: 4rpx;
  line-height: 1.3;
}
.stat.sub {
  font-size: 18rpx;
  color: #757575;
}
.bottom-panel {
  flex-shrink: 0;
  max-height: 38vh;
  margin-top: 10rpx;
}
.log-card {
  background: #fff;
  border-radius: 10rpx;
  padding: 12rpx 16rpx;
  margin-bottom: 10rpx;
  border: 1px solid #e0e0e0;
}
.log-title {
  font-size: 22rpx;
  font-weight: 700;
  color: #1b5e20;
  margin-bottom: 4rpx;
  display: block;
}
.log-line {
  display: block;
  font-size: 20rpx;
  color: #424242;
  line-height: 1.4;
  margin-top: 2rpx;
}
.actions {
  background: #fff;
  border-radius: 12rpx;
  padding: 16rpx;
  border: 1px solid #c8e6c9;
}
.actions-title {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #1b5e20;
  margin-bottom: 10rpx;
}
.action-group {
  margin-bottom: 8rpx;
}
.group-label {
  display: block;
  font-size: 22rpx;
  color: #616161;
  margin-bottom: 6rpx;
}
.btn {
  margin-top: 8rpx;
  border-radius: 10rpx;
  font-size: 26rpx;
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
.hint {
  display: block;
  font-size: 20rpx;
  color: #757575;
  margin-top: 10rpx;
  line-height: 1.4;
}
.result-card {
  background: #e8f5e9;
  border-radius: 12rpx;
  padding: 20rpx;
  text-align: center;
}
.result-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1b5e20;
  display: block;
}
.result-winner {
  font-size: 24rpx;
  color: #212121;
  margin: 12rpx 0 16rpx;
  display: block;
}
.err {
  color: #c62828;
  font-size: 24rpx;
  margin-top: 8rpx;
  flex-shrink: 0;
}
</style>
