import { ref, onMounted, onUnmounted } from "vue";

const DEFAULT_THRESHOLD = 768;

/** 宽屏（电脑/平板横屏）检测，用于放大棋盘中央信息字号 */
export function useLargeScreen(threshold = DEFAULT_THRESHOLD) {
  const isLargeScreen = ref(false);

  function refresh() {
    try {
      const info = uni.getSystemInfoSync();
      isLargeScreen.value = info.windowWidth >= threshold;
    } catch {
      if (typeof window !== "undefined") {
        isLargeScreen.value = window.innerWidth >= threshold;
      }
    }
  }

  onMounted(() => {
    refresh();
    if (typeof window !== "undefined") {
      window.addEventListener("resize", refresh);
    }
  });

  onUnmounted(() => {
    if (typeof window !== "undefined") {
      window.removeEventListener("resize", refresh);
    }
  });

  return { isLargeScreen, refresh };
}
