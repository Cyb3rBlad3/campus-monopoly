<template>
  <view class="page">
    <view class="hero">
      <text class="title">CampusMonopoly</text>
      <text class="subtitle">校园版大富翁 · H5</text>
    </view>
    <view class="actions">
      <button class="btn primary" @click="goCreate">
        创建 / 加入房间
      </button>
      <button
        v-if="session.gameId"
        class="btn"
        @click="goBoard"
      >
        继续对局
      </button>
    </view>
    <view class="tips">
      <text class="tip-line">
        接口基址：{{ apiBase || "（未配置，见 .env.development）" }}
      </text>
      <text class="tip-line">规则与数据结构见仓库根目录规则文档。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSessionStore } from "../../stores/session";
import { getApiBaseUrl } from "../../config/env";

const session = useSessionStore();
const apiBase = computed(() => getApiBaseUrl());

function goCreate() {
  uni.navigateTo({ url: "/pages/room/create" });
}

function goBoard() {
  uni.navigateTo({ url: "/pages/game/board" });
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 48rpx 40rpx;
  box-sizing: border-box;
  background: linear-gradient(180deg, #e8f5e9 0%, #f5faf6 40%);
}
.hero {
  margin-top: 80rpx;
  margin-bottom: 80rpx;
}
.title {
  display: block;
  font-size: 52rpx;
  font-weight: 700;
  color: #1b5e20;
  letter-spacing: 2rpx;
}
.subtitle {
  display: block;
  margin-top: 16rpx;
  font-size: 28rpx;
  color: #558b2f;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.btn {
  border-radius: 16rpx;
}
.btn.primary {
  background-color: #2e7d32;
}
.tips {
  margin-top: 64rpx;
  padding: 24rpx;
  background: rgba(255, 255, 255, 0.85);
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
