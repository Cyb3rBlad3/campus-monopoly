<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { watch } from "vue";
import { useNetworkStore } from "./stores/network";
import { useRoomSession } from "./composables/useRoomSession";

const network = useNetworkStore();
const { tryAutoReconnect } = useRoomSession();

onLaunch(() => {
  network.init();
});

onShow(() => {
  network.syncFromNavigator();
  if (network.isOnline) {
    tryAutoReconnect();
  }
});

watch(
  () => network.isOnline,
  (online, wasOnline) => {
    if (online && wasOnline === false) {
      tryAutoReconnect();
    }
  }
);

onHide(() => {
  console.log("App Hide");
});
</script>

<style></style>
