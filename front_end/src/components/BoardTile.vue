<template>
  <view
    class="board-tile"
    :class="[typeClass, { 'board-tile--active': isActive, 'board-tile--large': large }]"
  >
    <image
      v-if="tile.icon"
      class="tile-icon"
      :src="tileIconPath(tile.icon)"
      mode="aspectFit"
    />
    <text class="tile-name">{{ tile.name }}</text>
    <text v-if="tile.cost > 0" class="tile-cost">¥{{ tile.cost }}</text>
    <view v-if="players.length" class="tile-pieces">
      <view
        v-for="(item, index) in playerItems"
        :key="item.player.id"
        class="tile-piece"
        :class="[
          pieceStackClass(index, players.length),
          {
            'tile-piece--current': item.isCurrent,
            'tile-piece--me': item.isMe,
          },
        ]"
        :style="{ background: item.color }"
      >
        <text class="tile-piece-text">{{ item.initial }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Player, Tile } from "../types/game";
import { tileIconPath } from "../utils/gameLabels";
import {
  TILE_TYPE_CLASS,
  pieceStackClass,
  playerInitial,
  resolvePieceColor,
} from "../utils/boardLayout";

const props = defineProps<{
  tile: Tile;
  players: Player[];
  allPlayers: Player[];
  currentPlayerId: string;
  localPlayerId: string;
  isActive?: boolean;
  large?: boolean;
}>();

const typeClass = computed(
  () => TILE_TYPE_CLASS[props.tile.type] ?? "tile--special"
);

const playerItems = computed(() =>
  props.players.map((player) => ({
    player,
    color: resolvePieceColor(
      player,
      props.allPlayers.findIndex((p) => p.id === player.id)
    ),
    initial: playerInitial(player.name),
    isCurrent: player.id === props.currentPlayerId,
    isMe: player.id === props.localPlayerId,
  }))
);
</script>

<style scoped>
.board-tile {
  position: relative;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-width: 0;
  min-height: 0;
  height: 100%;
  padding: 4rpx 2rpx 6rpx;
  border-radius: 10rpx;
  border: 2rpx solid #d2e2dc;
  overflow: hidden;
}
.board-tile--active {
  border-color: #2e7d32;
  box-shadow: inset 0 0 0 2rpx rgba(46, 125, 50, 0.25);
}
.tile--income {
  background: #e9fbf2;
}
.tile--expense {
  background: #fff3ef;
}
.tile--social {
  background: #eef6ff;
}
.tile--saving {
  background: #fff8e6;
}
.tile--special {
  background: #f5efff;
}
.tile-icon {
  width: 45rpx;
  height: 45rpx;
  flex-shrink: 0;
}
.tile-name {
  font-size: 16rpx;
  font-weight: 700;
  color: #183934;
  text-align: center;
  line-height: 1.15;
  margin-top: 2rpx;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tile-cost {
  font-size: 14rpx;
  color: #c62828;
  line-height: 1.1;
}
.tile-pieces {
  margin-top: auto;
  width: 100%;
  min-height: 28rpx;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  align-content: center;
  gap: 4rpx;
  padding-top: 2rpx;
}
.tile-piece {
  width: 26rpx;
  height: 26rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.18);
  flex-shrink: 0;
}
.tile-piece--current {
  box-shadow: 0 0 0 3rpx rgba(242, 183, 53, 0.95);
}
.tile-piece--me {
  box-shadow: 0 0 0 2rpx #fff, 0 0 0 4rpx rgba(46, 125, 50, 0.85);
}
.tile-piece-text {
  font-size: 14rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}
/* 同格多人错开 */
.piece--stack-2-1 {
  transform: translateX(-4rpx);
}
.piece--stack-2-2 {
  transform: translateX(4rpx);
}
.piece--stack-3-1 {
  transform: translate(-4rpx, -2rpx);
}
.piece--stack-3-2 {
  transform: translate(4rpx, -2rpx);
}
.piece--stack-3-3 {
  transform: translateY(4rpx);
}
.piece--stack-4-1 {
  transform: translate(-4rpx, -3rpx);
}
.piece--stack-4-2 {
  transform: translate(4rpx, -3rpx);
}
.piece--stack-4-3 {
  transform: translate(-4rpx, 3rpx);
}
.piece--stack-4-4 {
  transform: translate(4rpx, 3rpx);
}
.board-tile--large .tile-icon {
  width: 55rpx;
  height: 55rpx;
}
.board-tile--large .tile-name {
  font-size: 20rpx;
}
.board-tile--large .tile-cost {
  font-size: 16rpx;
}
.board-tile--large .tile-piece {
  width: 32rpx;
  height: 32rpx;
}
.board-tile--large .tile-piece-text {
  font-size: 16rpx;
}
</style>
