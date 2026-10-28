# ==================================================================================
from __future__ import annotations

# ==================================================================================
from uuid import UUID

# ==================================================================================
from jAGFx.IPC import Message
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
class HelloMessage(Message):
    """Client → main. Establishes peer alive state for ownerId (client bridgeId)."""

    def __init__(
        self,
        payload: iSerializable | None = None,
        correlationId: UUID | None = None,
        isTerminal: bool = False,
        timestamp: float | None = None,
        ownerId: UUID | None = None,
    ) -> None:
        super().__init__(
            payload=payload,
            correlationId=correlationId,
            isTerminal=isTerminal,
            timestamp=timestamp,
            ownerId=ownerId,
        )


class HelloAckMessage(Message):
    """Main → client. Confirms Hello; only control reply used to complete handshake."""

    def __init__(
        self,
        payload: iSerializable | None = None,
        correlationId: UUID | None = None,
        isTerminal: bool = False,
        timestamp: float | None = None,
        ownerId: UUID | None = None,
    ) -> None:
        super().__init__(
            payload=payload,
            correlationId=correlationId,
            isTerminal=isTerminal,
            timestamp=timestamp,
            ownerId=ownerId,
        )


class HeartbeatMessage(Message):
    """Client → main. Refreshes peer alive expiry for ownerId (client bridgeId)."""

    def __init__(
        self,
        payload: iSerializable | None = None,
        correlationId: UUID | None = None,
        isTerminal: bool = False,
        timestamp: float | None = None,
        ownerId: UUID | None = None,
    ) -> None:
        super().__init__(
            payload=payload,
            correlationId=correlationId,
            isTerminal=isTerminal,
            timestamp=timestamp,
            ownerId=ownerId,
        )


# ==================================================================================
__all__ = ["HelloMessage", "HelloAckMessage", "HeartbeatMessage"]
