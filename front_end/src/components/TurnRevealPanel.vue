<template>
  <view class="turn-reveal">
    <view class="reveal-head">
      <text class="reveal-step">
        {{ stepLabel }}
      </text>
      <text class="reveal-skip" @click="emit('skip')">跳过</text>
    </view>

    <view v-if="phase === 'dice'" class="reveal-body dice-stage">
      <text class="dice-caption">{{ playerName }} 掷骰中…</text>
      <view class="dice-wrap">
        <view class="dice" :class="{ 'dice--landed': diceLanded }">
          <text class="dice-face">{{ displayDice }}</text>
        </view>
      </view>
    </view>

    <view v-else-if="phase === 'passive' && passiveMeta" class="reveal-body card-stage">
      <text class="stage-tag passive">被动事件</text>
      <view class="intro-card">
        <image
          class="intro-icon"
          :src="passiveMeta.iconPath"
          mode="aspectFit"
        />
        <view class="intro-text">
          <text class="intro-name">{{ passiveMeta.name }}</text>
          <text class="intro-desc">{{ passiveMeta.description }}</text>
        </view>
      </view>
    </view>

    <view v-else-if="phase === 'card' && cardMeta" class="reveal-body card-stage">
      <text class="stage-tag action">行动牌</text>
      <view class="intro-card">
        <image
          class="intro-icon"
          :src="cardMeta.iconPath"
          mode="aspectFit"
        />
        <view class="intro-text">
          <text class="intro-name">{{ cardMeta.name }}</text>
          <text class="intro-desc">{{ cardMeta.description }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from "vue";
import type { RevealPhase } from "../composables/useTurnReveal";
import type { CardRevealMeta } from "../utils/gameLabels";

const props = defineProps<{
  phase: RevealPhase;
  playerName: string;
  dice: number;
  passiveMeta: CardRevealMeta | null;
  cardMeta: CardRevealMeta | null;
  stepIndex: number;
  stepTotal: number;
}>();

const emit = defineEmits<{
  skip: [];
}>();

const rollingFace = ref(1);
const diceLanded = ref(false);
let rollTimer: ReturnType<typeof setInterval> | null = null;
let landTimer: ReturnType<typeof setTimeout> | null = null;

const displayDice = computed(() =>
  diceLanded.value ? props.dice : rollingFace.value
);

const stepLabel = computed(() => {
  if (props.phase === "dice") return `掷骰 ${props.stepIndex}/${props.stepTotal}`;
  if (props.phase === "passive") return `被动 ${props.stepIndex}/${props.stepTotal}`;
  if (props.phase === "card") return `抽牌 ${props.stepIndex}/${props.stepTotal}`;
  return "";
});

function clearDiceTimers() {
  if (rollTimer) {
    clearInterval(rollTimer);
    rollTimer = null;
  }
  if (landTimer) {
    clearTimeout(landTimer);
    landTimer = null;
  }
}

function startDiceRoll() {
  clearDiceTimers();
  diceLanded.value = false;
  rollingFace.value = Math.floor(Math.random() * 6) + 1;
  rollTimer = setInterval(() => {
    rollingFace.value = Math.floor(Math.random() * 6) + 1;
  }, 80);
  landTimer = setTimeout(() => {
    clearDiceTimers();
    diceLanded.value = true;
  }, 1000);
}

watch(
  () => props.phase,
  (phase) => {
    if (phase === "dice") {
      startDiceRoll();
    } else {
      clearDiceTimers();
      diceLanded.value = false;
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  clearDiceTimers();
});
</script>

<style scoped>
.turn-reveal {
  background: linear-gradient(180deg, #e8f5e9 0%, #fff 100%);
  border-radius: 10rpx;
  padding: 12rpx 14rpx;
  margin-bottom: 8rpx;
  border: 1px solid #c8e6c9;
}
.reveal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8rpx;
}
.reveal-step {
  font-size: 20rpx;
  font-weight: 700;
  color: #2e7d32;
}
.reveal-skip {
  font-size: 20rpx;
  color: #757575;
  padding: 4rpx 8rpx;
}
.reveal-body {
  min-height: 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.dice-stage {
  padding: 8rpx 0 4rpx;
}
.dice-caption {
  font-size: 22rpx;
  color: #424242;
  margin-bottom: 10rpx;
}
.dice-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}
.dice {
  width: 88rpx;
  height: 88rpx;
  border-radius: 14rpx;
  background: #fff;
  border: 2px solid #2e7d32;
  box-shadow: 0 6rpx 16rpx rgba(46, 125, 50, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: diceShake 0.12s linear infinite;
}
.dice--landed {
  animation: diceLand 0.25s ease-out forwards;
}
.dice-face {
  font-size: 44rpx;
  font-weight: 700;
  color: #1b5e20;
  line-height: 1;
}
.card-stage {
  align-items: stretch;
  padding: 4rpx 0;
}
.stage-tag {
  align-self: flex-start;
  font-size: 18rpx;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
  margin-bottom: 8rpx;
}
.stage-tag.passive {
  background: #fff3e0;
  color: #e65100;
}
.stage-tag.action {
  background: #e3f2fd;
  color: #1565c0;
}
.intro-card {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  width: 100%;
}
.intro-icon {
  width: 72rpx;
  height: 72rpx;
  flex-shrink: 0;
  border-radius: 10rpx;
  background: #fff;
  border: 1px solid #e0e0e0;
}
.intro-text {
  flex: 1;
  min-width: 0;
}
.intro-name {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #1b5e20;
  margin-bottom: 4rpx;
}
.intro-desc {
  display: block;
  font-size: 20rpx;
  color: #616161;
  line-height: 1.4;
}

@keyframes diceShake {
  0% {
    transform: rotate(-8deg) scale(1);
  }
  25% {
    transform: rotate(8deg) scale(1.04);
  }
  50% {
    transform: rotate(-6deg) scale(0.98);
  }
  75% {
    transform: rotate(6deg) scale(1.02);
  }
  100% {
    transform: rotate(-8deg) scale(1);
  }
}

@keyframes diceLand {
  0% {
    transform: scale(1.12);
  }
  100% {
    transform: scale(1);
  }
}

@media (min-width: 768px) {
  .turn-reveal {
    padding: 14px 16px;
    margin-bottom: 10px;
  }
  .reveal-step,
  .reveal-skip {
    font-size: 14px;
  }
  .dice-caption {
    font-size: 15px;
  }
  .dice {
    width: 64px;
    height: 64px;
    border-radius: 10px;
  }
  .dice-face {
    font-size: 32px;
  }
  .stage-tag {
    font-size: 12px;
    padding: 2px 8px;
  }
  .intro-icon {
    width: 56px;
    height: 56px;
  }
  .intro-name {
    font-size: 17px;
  }
  .intro-desc {
    font-size: 14px;
    line-height: 1.45;
  }
  .reveal-body {
    min-height: 96px;
  }
}
</style>
