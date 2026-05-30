<template>
  <view class="composed-board" :class="{ 'composed-board--large': isLargeScreen }">
    <view class="board-grid">
      <BoardTile
        v-for="tile in orderedTiles"
        :key="tile.id"
        class="grid-tile"
        :style="tileGridStyle(tile.position)"
        :tile="tile"
        :players="playersOnTile(tile.position)"
        :all-players="players"
        :current-player-id="currentPlayerId"
        :local-player-id="localPlayerId"
        :large="isLargeScreen"
        :is-active="
          currentPlayer != null &&
          normalizeBoardPosition(currentPlayer.position) ===
            normalizeBoardPosition(tile.position)
        "
      />
      <view class="grid-hub">
        <BoardCenterPlayers
          :players="players"
          :round="round"
          :public-reserve="publicReserve"
          :current-player-id="currentPlayerId"
          :local-player-id="localPlayerId"
        />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Player, Tile } from "../types/game";
import BoardCenterPlayers from "./BoardCenterPlayers.vue";
import BoardTile from "./BoardTile.vue";
import { useLargeScreen } from "../composables/useLargeScreen";
import {
  groupPlayersByTile,
  normalizeBoardPosition,
  tileGridStyle,
} from "../utils/boardLayout";

const props = defineProps<{
  board: Tile[];
  players: Player[];
  round: number;
  publicReserve: number;
  currentPlayerId: string;
  localPlayerId: string;
}>();

const { isLargeScreen } = useLargeScreen();

const orderedTiles = computed(() =>
  [...props.board].sort((a, b) => a.position - b.position)
);

const playersByTile = computed(() => groupPlayersByTile(props.players));

const currentPlayer = computed(
  () => props.players.find((p) => p.id === props.currentPlayerId) ?? null
);

function playersOnTile(position: number): Player[] {
  return playersByTile.value.get(normalizeBoardPosition(position)) ?? [];
}
</script>

<style scoped>
.composed-board {
  width: 100%;
  height: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.board-grid {
  width: 100%;
  max-height: 100%;
  aspect-ratio: 1;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(5, 1fr);
  gap: 6rpx;
  padding: 8rpx;
  box-sizing: border-box;
  background: #e8f5e9;
  border-radius: 16rpx;
  border: 2rpx solid #b9dcca;
}
.grid-tile {
  min-width: 0;
  min-height: 0;
}
.grid-hub {
  grid-row: 2 / 5;
  grid-column: 2 / 5;
  min-width: 0;
  min-height: 0;
  display: flex;
}
.composed-board--large .board-grid {
  gap: 8rpx;
  padding: 10rpx;
}
</style>
