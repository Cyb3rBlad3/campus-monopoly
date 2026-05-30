<template>
  <view
    class="piece-marker"
    :class="{
      current: isCurrent,
      me: isMe,
      stacked: stackTotal > 1,
    }"
    :style="markerStyle"
  >
    <svg
      class="piece-svg"
      viewBox="-54 -108 108 108"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <ellipse class="piece-shadow" cx="0" cy="43" rx="37" ry="9" />
      <path
        class="piece-body"
        :fill="color"
        :stroke="isMe ? '#ffffff' : 'none'"
        :stroke-width="isMe ? 3 : 0"
        d="M0 -54 c31 0 54 23 54 53 0 41 -54 83 -54 83 S-54 40 -54 -1 c0 -30 23 -53 54 -53z"
      />
      <circle class="piece-face" cx="0" cy="-4" r="25" />
      <text class="piece-initial" x="0" y="3">{{ initial }}</text>
    </svg>
    <text v-if="showName" class="piece-name">{{ player.name }}</text>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { CSSProperties } from "vue";
import type { Player } from "../types/game";

const props = withDefaults(
  defineProps<{
    player: Player;
    color: string;
    positionStyle: { left: string; top: string; zIndex: number };
    isCurrent?: boolean;
    isMe?: boolean;
    stackIndex?: number;
    stackTotal?: number;
    showName?: boolean;
  }>(),
  {
    isCurrent: false,
    isMe: false,
    stackIndex: 0,
    stackTotal: 1,
    showName: true,
  }
);

const initial = computed(() => {
  const name = props.player.name.trim();
  return name ? name.charAt(0) : "?";
});

const markerStyle = computed((): CSSProperties => ({
  left: props.positionStyle.left,
  top: props.positionStyle.top,
  zIndex: props.positionStyle.zIndex,
}));
</script>

<style scoped>
.piece-marker {
  position: absolute;
  width: 7%;
  min-width: 40rpx;
  max-width: 64rpx;
  transform: translate(-50%, -96%);
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
  filter: drop-shadow(0 4rpx 6rpx rgba(0, 0, 0, 0.18));
}
.piece-marker.stacked {
  width: 5.5%;
  min-width: 34rpx;
  max-width: 52rpx;
}
.piece-marker.current {
  filter: drop-shadow(0 0 10rpx rgba(242, 183, 53, 0.95));
}
.piece-svg {
  width: 100%;
  aspect-ratio: 54 / 108;
  display: block;
}
.piece-shadow {
  fill: #c9d8d2;
  opacity: 0.45;
}
.piece-face {
  fill: #fff;
  opacity: 0.95;
}
.piece-initial {
  font-family: "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif;
  font-size: 22px;
  font-weight: 700;
  fill: #31433e;
  text-anchor: middle;
}
.piece-name {
  margin-top: 2rpx;
  max-width: 120rpx;
  font-size: 18rpx;
  line-height: 1.2;
  color: #173a35;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: rgba(255, 255, 255, 0.88);
  border-radius: 8rpx;
  padding: 2rpx 8rpx;
}
</style>
