import { defineStore } from "pinia";
import { ref } from "vue";

/** H5 / uni 网络在线状态 */
export const useNetworkStore = defineStore("network", () => {
  const isOnline = ref(true);
  const networkType = ref("unknown");
  let inited = false;

  function syncFromNavigator() {
    if (typeof navigator !== "undefined" && "onLine" in navigator) {
      isOnline.value = navigator.onLine;
    }
  }

  function init() {
    if (inited) return;
    inited = true;
    syncFromNavigator();

    uni.getNetworkType({
      success(res) {
        networkType.value = res.networkType;
        isOnline.value = res.networkType !== "none";
      },
    });

    uni.onNetworkStatusChange((res) => {
      isOnline.value = res.isConnected;
      networkType.value = res.networkType;
    });

    if (typeof window !== "undefined") {
      window.addEventListener("online", () => {
        isOnline.value = true;
      });
      window.addEventListener("offline", () => {
        isOnline.value = false;
      });
    }
  }

  function assertOnline(): boolean {
    syncFromNavigator();
    if (!isOnline.value) {
      uni.showToast({ title: "网络已断开，请检查连接", icon: "none" });
      return false;
    }
    return true;
  }

  return {
    isOnline,
    networkType,
    init,
    syncFromNavigator,
    assertOnline,
  };
});
