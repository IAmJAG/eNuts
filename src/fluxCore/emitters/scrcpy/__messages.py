# ==================================================================================
from __future__ import annotations

# ==================================================================================
from uuid import UUID

# ==================================================================================
from jAGFx.IPC import Message
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from ...devices import SCRCPY
from .__footprint import SCRCPYError
from .__payloads import ScrcpyInitParams


# ==================================================================================
class ScrcpyInitializeMessage(Message):
    """Main → client. Correlated initialize command."""

    def __init__(
        self,
        payload: ScrcpyInitParams | None = None,
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


class ScrcpyStartMessage(Message):
    """Main → client. Start the emitter service (fire-and-forget)."""

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


class ScrcpyStopMessage(Message):
    """Main → client. Stop the emitter service (fire-and-forget)."""

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


class ScrcpyMetadataMessage(Message):
    """Client → main. Device/stream metadata snapshot (base SCRCPY)."""

    def __init__(
        self,
        payload: SCRCPY | None = None,
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


class ScrcpyErrorMessage(Message):
    """Client → main. Error detail; use isTerminal when ending an initialize conversation."""

    def __init__(
        self,
        payload: SCRCPYError | None = None,
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
__all__ = [
    "ScrcpyInitializeMessage",
    "ScrcpyStartMessage",
    "ScrcpyStopMessage",
    "ScrcpyMetadataMessage",
    "ScrcpyErrorMessage",
]
