const DEVICE_STORAGE_KEY = "campus_monopoly_device_id";
const DEVICE_COOKIE_KEY = "cm_device_id";
const ROOM_BINDINGS_KEY = "campus_monopoly_room_bindings";
const COOKIE_MAX_AGE_SEC = 365 * 24 * 60 * 60;

export interface RoomDeviceBinding {
  playerName: string;
  playerId: string;
  deviceId: string;
}

type BindingMap = Record<string, RoomDeviceBinding>;

function randomDeviceId(): string {
  const part = Math.random().toString(36).slice(2, 12);
  const ts = Date.now().toString(36);
  return `dev_${ts}_${part}`;
}

/** H5 下同步写入 Cookie，便于同源多标签页共享设备 ID */
function persistDeviceCookie(deviceId: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${DEVICE_COOKIE_KEY}=${encodeURIComponent(deviceId)}; path=/; max-age=${COOKIE_MAX_AGE_SEC}; SameSite=Lax`;
}

function readDeviceCookie(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(
    new RegExp(`(?:^|; )${DEVICE_COOKIE_KEY}=([^;]*)`)
  );
  return match ? decodeURIComponent(match[1]) : "";
}

/** 本机唯一设备 ID（localStorage + Cookie） */
export function getDeviceId(): string {
  try {
    let id = String(uni.getStorageSync(DEVICE_STORAGE_KEY) || "").trim();
    if (!id) {
      id = readDeviceCookie();
    }
    if (!id) {
      id = randomDeviceId();
    }
    uni.setStorageSync(DEVICE_STORAGE_KEY, id);
    persistDeviceCookie(id);
    return id;
  } catch {
    return randomDeviceId();
  }
}

function loadBindings(): BindingMap {
  try {
    const raw = uni.getStorageSync(ROOM_BINDINGS_KEY);
    if (!raw) return {};
    return JSON.parse(String(raw)) as BindingMap;
  } catch {
    return {};
  }
}

function saveBindings(map: BindingMap) {
  try {
    uni.setStorageSync(ROOM_BINDINGS_KEY, JSON.stringify(map));
  } catch {
    /* ignore */
  }
}

export function getRoomBinding(roomId: string): RoomDeviceBinding | null {
  if (!roomId) return null;
  return loadBindings()[roomId] ?? null;
}

export function setRoomBinding(
  roomId: string,
  binding: Omit<RoomDeviceBinding, "deviceId">
) {
  if (!roomId) return;
  const map = loadBindings();
  map[roomId] = { ...binding, deviceId: getDeviceId() };
  saveBindings(map);
}

export function clearRoomBinding(roomId: string) {
  if (!roomId) return;
  const map = loadBindings();
  delete map[roomId];
  saveBindings(map);
}

/** 本机是否已在该房间绑定其他昵称 */
export function assertLocalDeviceCanUseName(
  roomId: string,
  name: string
): string | null {
  const binding = getRoomBinding(roomId);
  if (!binding) return null;
  const key = name.trim().toLowerCase();
  const bound = binding.playerName.trim().toLowerCase();
  if (key && bound && key !== bound) {
    return `本机已以「${binding.playerName}」加入该房间，请使用该昵称重连`;
  }
  return null;
}

export function withDeviceId<T extends Record<string, unknown>>(
  body: T
): T & { deviceId: string } {
  return { ...body, deviceId: getDeviceId() };
}
