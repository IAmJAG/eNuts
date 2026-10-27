# ==================================================================================
"""Smoke: Endpoint + Bridge type dispatch and terminal correlation lifecycle.

Handlers are keyed by message type (see Bridge.messageHandlers), not payload
string kinds. Distinct conversation shapes use Message subclasses when needed.
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
def test_endpoint_bridge_type_dispatch() -> None:
    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge)

        await leftEndpoint.send(
            PingMessage(payload=SmokePayload(text="hello", kind="ping"))
        )
        await _waitFor(bridge._gotMessage)

        assert len(bridge.received) == 1
        assert bridge.received[0].payload.text == "hello"
        assert isinstance(bridge.received[0], PingMessage)

    asyncio.run(_withEndpoints(scenario))


def test_endpoint_terminal_clears_correlation() -> None:
    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge)

        correlationId = uuid4()
        bridge.registerProcessor(correlationId, bridge._onProcessor)
        rightEndpoint.bindCorrelation(correlationId, bridge)

        assert rightEndpoint.hasCorrelation(correlationId)
        assert bridge.hasProcessor(correlationId)

        await leftEndpoint.send(
            PingMessage(
                payload=SmokePayload(text="done", kind="ping"),
                correlationId=correlationId,
                isTerminal=True,
            )
        )
        await _waitFor(bridge._gotMessage)

        assert not rightEndpoint.hasCorrelation(correlationId)
        assert not bridge.hasProcessor(correlationId)
        assert len(bridge.processorHits) == 1
        assert bridge.processorHits[0].payload.text == "done"

    asyncio.run(_withEndpoints(scenario))


def test_register_bridge_rejects_duplicate_type() -> None:
    left, right = IOQueue.createPair()
    endpoint = Endpoint(IOQueue(outboundQueue=left, inboundQueue=right))

    first = RecordingBridge(PingMessage)
    second = RecordingBridge(PingMessage)
    endpoint.registerBridge(first)

    try:
        endpoint.registerBridge(second)
        raised = False
    except ValueError:
        raised = True

    assert raised is True


def test_unknown_message_type_is_ignored() -> None:
    """No registered handler for Message; PingMessage bridge must not receive it."""

    async def scenario(leftEndpoint: Endpoint, rightEndpoint: Endpoint) -> None:
        bridge = RecordingBridge(PingMessage)
        rightEndpoint.registerBridge(bridge)

        await leftEndpoint.send(
            Message(payload=SmokePayload(text="ignored", kind="other"))
        )
        await asyncio.sleep(0.15)

        assert bridge.received == []
        assert bridge.processorHits == []

    asyncio.run(_withEndpoints(scenario))
