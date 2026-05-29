<template>
  <view v-if="!network.isOnline" class="offline-banner">
    <text>网络已断开，部分功能不可用。恢复后将自动尝试重连。</text>
  </view>
</template>

<script setup lang="ts">
import { useNetworkStore } from "../stores/network";

const network = useNetworkStore();
</script>

<style scoped>
.offline-banner {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 16rpx 24rpx;
  background: #ffebee;
  color: #c62828;
  font-size: 24rpx;
  line-height: 1.4;
  border-bottom: 1px solid #ef9a9a;
}
</style>
