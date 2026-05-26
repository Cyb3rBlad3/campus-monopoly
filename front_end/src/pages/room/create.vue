<template>
  <view class="page">
    <view class="field">
      <text class="label">房间 ID（联调时由后端返回或手动填写）</text>
      <input
        v-model="roomIdInput"
        class="input"
        placeholder="例如 dorm_301"
      />
    </view>
    <view class="field">
      <text class="label">对局 gameId（开局后填写，用于拉取状态）</text>
      <input
        v-model="gameIdInput"
        class="input"
        placeholder="例如 game_001"
      />
    </view>
    <button class="btn primary" @click="saveSession">保存到本地会话</button>
    <button class="btn ghost" @click="goBoard">进入棋盘页</button>
    <view class="note">
      <text>
        创建房间、加入玩家、开局等请调用 `src/api/game.ts` 中方法与后端联调；此处仅保存会话字段便于 H5 调试。
      </text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSessionStore } from "../../stores/session";

const session = useSessionStore();
const roomIdInput = ref("");
const gameIdInput = ref("");

onMounted(() => {
  roomIdInput.value = session.roomId;
  gameIdInput.value = session.gameId;
});

function saveSession() {
  session.setRoom(roomIdInput.value.trim());
  session.setGame(gameIdInput.value.trim());
  uni.showToast({ title: "已保存", icon: "success" });
}

function goBoard() {
  if (!session.gameId) {
    uni.showToast({ title: "请先填写 gameId", icon: "none" });
    return;
  }
  uni.navigateTo({ url: "/pages/game/board" });
}
</script>

<style scoped>
.page {
  padding: 32rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
.field {
  margin-bottom: 32rpx;
}
.label {
  display: block;
  font-size: 26rpx;
  color: #424242;
  margin-bottom: 12rpx;
}
.input {
  width: 100%;
  padding: 20rpx 24rpx;
  border: 1px solid #c8e6c9;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
  background: #fff;
}
.btn {
  margin-top: 24rpx;
  border-radius: 12rpx;
}
.btn.primary {
  background-color: #2e7d32;
  color: #fff;
}
.btn.ghost {
  background: #fff;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}
.note {
  margin-top: 48rpx;
  font-size: 24rpx;
  color: #757575;
  line-height: 1.5;
}
</style>
