# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event

# ==================================================================================
from jAGFx.IPC import Bridge

# ==================================================================================
from .__messages import HeartbeatMessage, HelloAckMessage, HelloMessage


# ==================================================================================
class ControlBridge(Bridge):
    """Control-plane bridge: Hello / HelloAck / Heartbeat.

    Client originates Hello and Heartbeat (ownerId = client bridgeId).
    Main marks peer alive on Endpoint via markBridgeAlive.
    No separate session registry — only Endpoint._bridgeAlive keyed by bridgeId.
    """

    C_INITIAL_TTL_S: float = 5.0
    C_HEARTBEAT_TTL_S: float = 5.0

    def __init__(self) -> None:
        super().__init__()
        self._helloAcked: Event = Event()
        self._messageHandlers[HelloMessage] = self._onHello
        self._messageHandlers[HelloAckMessage] = self._onHelloAck
        self._messageHandlers[HeartbeatMessage] = self._onHeartbeat
        self._invalidateHandlerCache()

    @property
    def helloAcked(self) -> Event:
        return self._helloAcked

    async def _onHello(self, message: HelloMessage) -> None:
        ep = self._endpoint
        if ep is None:
            return

        peerId = message.ownerId
        if peerId is None:
            return

        ep.markBridgeAlive(peerId, self.C_INITIAL_TTL_S)

        ack = HelloAckMessage(correlationId=message.correlationId)
        ack.ownerId = peerId
        await self.send(ack)

    async def _onHelloAck(self, message: HelloAckMessage) -> None:
        self._helloAcked.set()

    async def _onHeartbeat(self, message: HeartbeatMessage) -> None:
        ep = self._endpoint
        if ep is None:
            return

        peerId = message.ownerId
        if peerId is None:
            return

        ep.markBridgeAlive(peerId, self.C_HEARTBEAT_TTL_S)


# ==================================================================================
__all__ = ["ControlBridge"]
