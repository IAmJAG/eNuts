# ==================================================================================
"""Smoke: Endpoint Bridge-ID routing and Bridge-owned correlation lifecycle.

Routing is by message.ownerId (or default Bridge). Correlation trackers and
terminal cleanup live entirely on the Bridge.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
from pathlib import Path
import sys
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC import Bridge, Endpoint, IOQueue, Message

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.ipc.payloads import SmokePayload  # noqa: E402


# ==================================================================================
class PingMessage(Message):
    """Distinct message type so type-keyed handlers can discriminate."""


class RecordingBridge(Bridge):
    def __init__(self, *messageTypes: type) -> None:
        super().__init__()
        self.received: list[Message] = []
        self.processorHits: list[Message] = []
        self._gotMessage = asyncio.Event()

        for messageType in messageTypes:
            self._messageHandlers[messageType] = self._onKind

    async def _onKind(self, message: Message) -> None:
        self.received.append(message)
        self._gotMessage.set()

    async def _onProcessor(self, message: Message) -> None:
        self.processorHits.append(message)
        self._gotMessage.set()


# ==================================================================================
async def _withEndpoints(work) -> None:
    left, right = IOQueue.createPair()
    leftEndpoint = Endpoint(IOQueue(outboundQueue=left, inboundQueue=right))
    rightEndpoint = Endpoint(IOQueue(outboundQueue=right, inboundQueue=left))

    await leftEndpoint.start()
    await rightEndpoint.start()
    try:
        await work(leftEndpoint, rightEndpoint)
    finally:
        await leftEndpoint.stop()
        await rightEndpoint.stop()


async def _waitFor(event: asyncio.Event, timeout: float = 1.0) -> None:
    await asyncio.wait_for(event.wait(), timeout=timeout)


# ==================================================================================
def test_default_bridge_receives_ownerless_message() -> None:
    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge, asDefault=True)

        await leftEndpoint.send(
            PingMessage(payload=SmokePayload(text="hello", kind="ping"))
        )
        await _waitFor(bridge._gotMessage)

        assert len(bridge.received) == 1
        assert bridge.received[0].payload.text == "hello"
        assert isinstance(bridge.received[0], PingMessage)

    asyncio.run(_withEndpoints(scenario))


def test_owner_id_routes_to_specific_bridge() -> None:
    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridgeA = RecordingBridge(PingMessage)
        bridgeB = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridgeA, asDefault=True)
        rightEndpoint.registerBridge(bridgeB)

        msg = PingMessage(
            payload=SmokePayload(text="targeted", kind="ping"),
            ownerId=bridgeB.bridgeId,
        )
        await leftEndpoint.send(msg)
        await _waitFor(bridgeB._gotMessage)

        assert len(bridgeB.received) == 1
        assert bridgeB.received[0].payload.text == "targeted"
        assert bridgeA.received == []

    asyncio.run(_withEndpoints(scenario))


def test_unknown_owner_is_dropped() -> None:
    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge, asDefault=True)

        await leftEndpoint.send(
            PingMessage(
                payload=SmokePayload(text="ghost", kind="ping"),
                ownerId=uuid4(),  # not registered
            )
        )
        await asyncio.sleep(0.15)

        assert bridge.received == []
        assert bridge.processorHits == []

    asyncio.run(_withEndpoints(scenario))


def test_terminal_clears_correlation_on_bridge() -> None:
    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge, asDefault=True)

        correlationId = uuid4()
        bridge.registerProcessor(correlationId, bridge._onProcessor)

        assert bridge.hasCorrelation(correlationId)
        assert bridge.hasProcessor(correlationId)

        await leftEndpoint.send(
            PingMessage(
                payload=SmokePayload(text="done", kind="ping"),
                correlationId=correlationId,
                isTerminal=True,
            )
        )
        await _waitFor(bridge._gotMessage)

        assert not bridge.hasCorrelation(correlationId)
        assert not bridge.hasProcessor(correlationId)
        assert len(bridge.processorHits) == 1
        assert bridge.processorHits[0].payload.text == "done"

    asyncio.run(_withEndpoints(scenario))


def test_register_bridge_rejects_duplicate_id() -> None:
    left, right = IOQueue.createPair()
    endpoint = Endpoint(IOQueue(outboundQueue=left, inboundQueue=right))

    first = RecordingBridge(PingMessage)
    second = RecordingBridge(PingMessage)
    # Force same bridgeId to test rejection
    second._bridgeId = first.bridgeId

    endpoint.registerBridge(first)

    try:
        endpoint.registerBridge(second)
        raised = False
    except ValueError:
        raised = True

    assert raised is True


def test_unregister_clears_default() -> None:
    left, right = IOQueue.createPair()
    endpoint = Endpoint(IOQueue(outboundQueue=left, inboundQueue=right))

    bridge = RecordingBridge(PingMessage)
    endpoint.registerBridge(bridge, asDefault=True)
    assert endpoint.defaultBridgeId == bridge.bridgeId

    endpoint.unregisterBridge(bridge)
    assert endpoint.defaultBridgeId is None


def test_type_handler_still_works_on_selected_bridge() -> None:
    """Message type dispatch remains inside the Bridge after owner routing."""

    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge, asDefault=True)

        await leftEndpoint.send(
            Message(payload=SmokePayload(text="ignored", kind="other"))
        )
        await asyncio.sleep(0.15)

        # Default Bridge received it but has no handler for base Message
        assert bridge.received == []
        assert bridge.processorHits == []

    asyncio.run(_withEndpoints(scenario))
