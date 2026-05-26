/** 后端 API 根地址，由 `.env.development` / `.env.production` 中 `VITE_API_BASE_URL` 注入 */
export function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL;
  return typeof base === "string" ? base.replace(/\/$/, "") : "";
}
