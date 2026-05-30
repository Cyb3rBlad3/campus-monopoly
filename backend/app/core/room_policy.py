"""房间大厅策略：等待房超时、设备绑定等。"""

from __future__ import annotations

# 等待中房间超过 15 分钟无更新则自动关闭（删除）
WAITING_ROOM_TTL_SECONDS = 900

# 玩家超过该秒数未重连/心跳则从房间踢出（等待房会同步 GameState）
PLAYER_PRESENCE_TTL_SECONDS = 60
