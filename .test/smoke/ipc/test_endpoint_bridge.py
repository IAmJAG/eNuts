# ==================================================================================
"""Smoke: Endpoint + Bridge kind dispatch and terminal correlation lifecycle."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
from pathlib import Path
import sys
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.IPC import Bridge, Endpoint, IOQueue, Message

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.ipc.payloads import SmokePayload  # noqa: E402


# ==================================================================================
class RecordingBridge(Bridge):
    def __init__(self, kinds: list[str]) -> None:
        super().__init__()
        self.received: list[Message] = []
        self.processorHits: list[Message] = []
        for kind in kinds:
            self._messageHandlers[kind] = self._onKind

    async def _onKind(self, message: Message) -> None:
        self.received.append(message)

    async def _onProcessor(self, message: Message) -> None:
        self.processorHits.append(message)


# ==================================================================================
async def _runEndpoints(
    leftEndpoint: Endpoint,
    rightEndpoint: Endpoint,
    work,
) -> None:
    await leftEndpoint.start()
    await rightEndpoint.start()
    try:
        await work()
        await asyncio.sleep(0.05)
    finally:
        await leftEndpoint.stop()
        await rightEndpoint.stop()


def test_endpoint_bridge_kind_dispatch() -> None:
    async def scenario() -> None:
        left, right = IOQueue.createPair()
        leftIo = IOQueue(outboundQueue=left, inboundQueue=right)
        rightIo = IOQueue(outboundQueue=right, inboundQueue=left)

        leftEndpoint = Endpoint(leftIo)
        rightEndpoint = Endpoint(rightIo)

        bridge = RecordingBridge(["ping"])
        rightEndpoint.registerBridge(bridge)

        async def work() -> None:
            msg = Message(payload=SmokePayload(text="hello", kind="ping"))
            await leftEndpoint.send(msg)
            for _ in range(50):
                if bridge.received:
                    break
                await asyncio.sleep(0.02)

            assert len(bridge.received) == 1
            assert bridge.received[0].payload.text == "hello"
            assert bridge.received[0].payload.kind == "ping"

        await _runEndpoints(leftEndpoint, rightEndpoint, work)

    asyncio.run(scenario())


def test_endpoint_terminal_clears_correlation() -> None:
    async def scenario() -> None:
        left, right = IOQueue.createPair()
        leftIo = IOQueue(outboundQueue=left, inboundQueue=right)
        rightIo = IOQueue(outboundQueue=right, inboundQueue=left)

        leftEndpoint = Endpoint(leftIo)
        rightEndpoint = Endpoint(rightIo)

        bridge = RecordingBridge(["ping"])
        rightEndpoint.registerBridge(bridge)

        correlationId = uuid4()

        async def work() -> None:
            bridge.registerProcessor(correlationId, bridge._onProcessor)
            rightEndpoint.bindCorrelation(correlationId, bridge)

            assert correlationId in rightEndpoint._correlations

            terminal = Message(
                payload=SmokePayload(text="done", kind="ping"),
                correlationId=correlationId,
                isTerminal=True,
            )
            await leftEndpoint.send(terminal)

            for _ in range(50):
                if bridge.received or bridge.processorHits:
                    break
                await asyncio.sleep(0.02)

            assert correlationId not in rightEndpoint._correlations
            assert correlationId not in bridge._processors
            assert len(bridge.processorHits) + len(bridge.received) >= 1

        await _runEndpoints(leftEndpoint, rightEndpoint, work)

    asyncio.run(scenario())


def test_register_bridge_rejects_duplicate_kind() -> None:
    left, right = IOQueue.createPair()
    io = IOQueue(outboundQueue=left, inboundQueue=right)
    endpoint = Endpoint(io)

    first = RecordingBridge(["ping"])
    second = RecordingBridge(["ping"])
    endpoint.registerBridge(first)

    try:
        endpoint.registerBridge(second)
        raised = False
    except ValueError:
        raised = True

    assert raised is True
