from __future__ import annotations

from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    maxPlayers: int = Field(default=4, ge=2, le=4)
    initialAllowance: int = Field(default=2000, ge=500, le=10000)


class JoinPlayerRequest(BaseModel):
    name: str = Field(default="玩家", min_length=1, max_length=32)
    deviceId: str = Field(min_length=8, max_length=128)
    avatarId: str | None = None
    pieceColor: str | None = None
    savingGoalType: str = Field(default="standard")


class StartRoomRequest(BaseModel):
    pass


class PlayerActionRequest(BaseModel):
    playerId: str


class RollRequest(PlayerActionRequest):
    dice: int | None = Field(default=None, ge=1, le=6)


class TileActionRequest(PlayerActionRequest):
    action: str
    targetPlayerId: str | None = None
    amount: int | None = Field(default=None, ge=1)


class UseCardRequest(PlayerActionRequest):
    cardId: str
    targetPlayerId: str | None = None


class EndTurnRequest(PlayerActionRequest):
    pass
