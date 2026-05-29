import type { GameState, TurnResult } from "../types/game";
import { getApiBaseUrl } from "../config/env";

export type ApiSuccess<T> = { ok: true; data: T };
export type ApiError = { ok: false; statusCode: number; message: string };
export type ApiResult<T> = ApiSuccess<T> | ApiError;

type RequestOptions = UniApp.RequestOptions;

function joinUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) {
    path = `/${path}`;
  }
  return base ? `${base}${path}` : path;
}

/** 与规则文档一致：写操作返回完整 GameState + 可选 TurnResult */
export type GameMutationResponse = {
  gameState: GameState;
  turnResult?: TurnResult | null;
};

function isBrowserOffline(): boolean {
  return typeof navigator !== "undefined" && navigator.onLine === false;
}

export async function apiRequest<T>(
  options: Omit<RequestOptions, "url"> & { url: string }
): Promise<ApiResult<T>> {
  if (isBrowserOffline()) {
    return { ok: false, statusCode: 0, message: "网络已断开，请检查连接" };
  }
  const url = joinUrl(options.url);
  return new Promise((resolve) => {
    uni.request({
      ...options,
      url,
      success(res) {
        const status = res.statusCode ?? 0;
        if (status >= 200 && status < 300) {
          resolve({ ok: true, data: res.data as T });
          return;
        }
        const msg =
          typeof res.data === "object" &&
          res.data !== null &&
          "message" in res.data
            ? String((res.data as { message: unknown }).message)
            : `HTTP ${status}`;
        resolve({ ok: false, statusCode: status, message: msg });
      },
      fail(err) {
        resolve({
          ok: false,
          statusCode: 0,
          message: err.errMsg || "网络请求失败",
        });
      },
    });
  });
}

export async function postJson<T>(
  path: string,
  body?: unknown
): Promise<ApiResult<T>> {
  return apiRequest<T>({
    url: path,
    method: "POST",
    header: {
      "Content-Type": "application/json",
    },
    data: body === undefined ? undefined : (body as Record<string, unknown>),
  });
}

export async function getJson<T>(path: string): Promise<ApiResult<T>> {
  return apiRequest<T>({
    url: path,
    method: "GET",
  });
}
