<template>
  <view class="center-hub" :class="{ 'center-hub--large': isLargeScreen }">
    <view class="hub-header">
      <text class="hub-meta">第 {{ round }} 回合</text>
      <text class="hub-meta">储备 ¥{{ publicReserve }}</text>
    </view>
    <view class="hub-grid" :class="gridClass">
      <view
        v-for="item in playerItems"
        :key="item.player.id"
        class="hub-card"
        :class="{
          current: item.isCurrent,
          me: item.isMe,
          bankrupt: item.player.bankrupt,
        }"
      >
        <view class="hub-card-head">
          <view class="mini-piece" :style="{ background: item.color }">
            <text class="mini-initial">{{ item.initial }}</text>
          </view>
          <text class="hub-name">{{ item.player.name }}</text>
          <view class="hub-tags">
            <text v-if="item.isMe" class="hub-tag me">我</text>
            <text v-if="item.isCurrent" class="hub-tag turn">回合</text>
          </view>
        </view>
        <text class="hub-stat">¥{{ item.player.money }} · 格{{ item.player.position + 1 }}</text>
        <text class="hub-sub">
          社交{{ item.player.socialValue }} 理财{{ item.player.financeValue }}
        </text>
        <text class="hub-sub">
          心情{{ item.player.mood }} 精力{{ item.player.energy }}
          <text v-if="item.player.handCards?.length">
            · 牌{{ item.player.handCards.length }}
          </text>
        </text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Player } from "../types/game";
import { playerInitial, resolvePieceColor } from "../utils/boardLayout";
import { useLargeScreen } from "../composables/useLargeScreen";

const props = defineProps<{
  players: Player[];
  round: number;
  publicReserve: number;
  currentPlayerId: string;
  localPlayerId: string;
}>();

const { isLargeScreen } = useLargeScreen();

const playerItems = computed(() =>
  props.players.map((player, index) => ({
    player,
    color: resolvePieceColor(player, index),
    initial: playerInitial(player.name),
    isCurrent: player.id === props.currentPlayerId,
    isMe: player.id === props.localPlayerId,
  }))
);

const gridClass = computed(() => {
  const count = props.players.length;
  if (count <= 2) return "cols-2";
  return "cols-2 rows-2";
});
</script>

<style scoped>
.center-hub {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 6rpx 8rpx;
  border-radius: 12rpx;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(136, 201, 170, 0.55);
  box-shadow: 0 2rpx 10rpx rgba(23, 58, 53, 0.06);
  overflow: hidden;
}
.hub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8rpx;
  padding: 0 4rpx 4rpx;
  border-bottom: 1px solid rgba(207, 226, 218, 0.9);
  flex-shrink: 0;
}
.hub-meta {
  font-size: 18rpx;
  color: #657a74;
  line-height: 1.2;
}
.hub-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  gap: 4rpx;
  padding-top: 4rpx;
}
.hub-grid.cols-2 {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr;
}
.hub-grid.rows-2 {
  grid-template-rows: 1fr 1fr;
}
.hub-card {
  min-width: 0;
  padding: 4rpx 6rpx;
  border-radius: 8rpx;
  background: rgba(245, 250, 248, 0.95);
  border: 1px solid rgba(210, 226, 220, 0.9);
  overflow: hidden;
}
.hub-card.current {
  border-color: #ffb74d;
  background: rgba(255, 248, 235, 0.98);
}
.hub-card.me {
  border-left: 3rpx solid #2e7d32;
}
.hub-card.bankrupt {
  opacity: 0.45;
}
.hub-card-head {
  display: flex;
  align-items: center;
  gap: 4rpx;
  min-width: 0;
}
.mini-piece {
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2rpx solid rgba(255, 255, 255, 0.9);
}
.mini-initial {
  font-size: 16rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}
.hub-name {
  flex: 1;
  min-width: 0;
  font-size: 20rpx;
  font-weight: 700;
  color: #173a35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hub-tags {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2rpx;
  flex-shrink: 0;
}
.hub-tag {
  font-size: 14rpx;
  line-height: 1.1;
  padding: 1rpx 6rpx;
  border-radius: 6rpx;
}
.hub-tag.me {
  color: #2e7d32;
  background: #c8e6c9;
}
.hub-tag.turn {
  color: #ef6c00;
  background: #ffe0b2;
}
.hub-stat {
  display: block;
  font-size: 18rpx;
  color: #212121;
  margin-top: 2rpx;
  line-height: 1.2;
}
.hub-sub {
  display: block;
  font-size: 15rpx;
  color: #757575;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.center-hub--large {
  padding: 8px 10px;
}
.center-hub--large .hub-meta {
  font-size: 16px;
}
.center-hub--large .mini-piece {
  width: 34px;
  height: 34px;
}
.center-hub--large .mini-initial {
  font-size: 15px;
}
.center-hub--large .hub-name {
  font-size: 20px;
}
.center-hub--large .hub-tag {
  font-size: 13px;
  padding: 2px 7px;
}
.center-hub--large .hub-stat {
  font-size: 17px;
}
.center-hub--large .hub-sub {
  font-size: 15px;
  white-space: normal;
}

@media (min-width: 768px) {
  .center-hub {
    padding: 10px 12px;
  }
  .hub-header {
    padding-bottom: 6px;
    margin-bottom: 2px;
  }
  .hub-meta {
    font-size: 16px;
  }
  .mini-piece {
    width: 34px;
    height: 34px;
  }
  .mini-initial {
    font-size: 15px;
  }
  .hub-name {
    font-size: 20px;
  }
  .hub-tag {
    font-size: 13px;
    padding: 2px 7px;
  }
  .hub-stat {
    font-size: 17px;
    margin-top: 4px;
  }
  .hub-sub {
    font-size: 15px;
    line-height: 1.35;
    white-space: normal;
  }
  .hub-card {
    padding: 6px 8px;
  }
  .hub-grid {
    gap: 6px;
    padding-top: 6px;
  }
}
</style>
