# ==================================================================================
"""Smoke: ScrcpyRealBridge + ScrcpyProxyBridge over paired Endpoints (no ADB)."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
from pathlib import Path
import sys

# ==================================================================================
from jAGFx.IPC import Endpoint, IOQueue

# ==================================================================================
_REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from fluxCore.devices import SCRCPY  # noqa: E402
from fluxCore.emitters.scrcpy import (  # noqa: E402
    ScrcpyInitParams,
    ScrcpyMetadataMessage,
    ScrcpyProxyBridge,
    ScrcpyRealBridge,
)


# ==================================================================================
class StubEmitter:
    """Minimal stand-in for SCRCPYEmitter (no ADB)."""

    def __init__(self, serial: str = "stub-device") -> None:
        self.id = serial
        self.name = "stub"
        self.codecId = "h264"
        self.width = 1080
        self.height = 1920
        self.started = False
        self._subs: dict[str, list] = {}

    def subscribe(self, event: str, callback) -> None:
        self._subs.setdefault(event, []).append(callback)

    async def initialize(self, GPUID: int = 0, GPUReady: bool = True) -> None:
        _ = (GPUID, GPUReady)

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False


class FailingEmitter(StubEmitter):
    async def initialize(self, GPUID: int = 0, GPUReady: bool = True) -> None:
        raise RuntimeError("simulated deploy failure")


# ==================================================================================
async def _withEndpoints(work) -> None:
    left, right = IOQueue.createPair()
    mainEp = Endpoint(IOQueue(outboundQueue=left, inboundQueue=right))
    clientEp = Endpoint(IOQueue(outboundQueue=right, inboundQueue=left))
    await mainEp.start()
    await clientEp.start()
    try:
        await work(mainEp, clientEp)
    finally:
        await mainEp.stop()
        await clientEp.stop()


# ==================================================================================
def test_initialize_success_delivers_metadata() -> None:
    async def scenario(mainEp: Endpoint, clientEp: Endpoint) -> None:
        stub = StubEmitter(serial="dev-1")
        real = ScrcpyRealBridge(emitter=stub)
        proxy = ScrcpyProxyBridge()
        clientEp.registerBridge(real, asDefault=True)
        mainEp.registerBridge(proxy, asDefault=True)

        await proxy.requestInitialize(ScrcpyInitParams(serial="dev-1"))
        await asyncio.wait_for(proxy.metadataEvent.wait(), timeout=2.0)

        assert proxy.lastMetadata is not None
        assert proxy.lastMetadata.width == 1080
        assert proxy.lastMetadata.height == 1920
        assert proxy.lastError is None

    asyncio.run(_withEndpoints(scenario))


def test_initialize_failure_delivers_error() -> None:
    async def scenario(mainEp: Endpoint, clientEp: Endpoint) -> None:
        real = ScrcpyRealBridge(emitter=FailingEmitter())
        proxy = ScrcpyProxyBridge()
        clientEp.registerBridge(real, asDefault=True)
        mainEp.registerBridge(proxy, asDefault=True)

        await proxy.requestInitialize(ScrcpyInitParams(serial="dev-x"))
        await asyncio.wait_for(proxy.errorEvent.wait(), timeout=2.0)

        assert proxy.lastError is not None
        assert "simulated deploy failure" in proxy.lastError.message
        assert proxy.lastError.phase == "initialize"

    asyncio.run(_withEndpoints(scenario))


def test_start_stop_reach_emitter() -> None:
    async def scenario(mainEp: Endpoint, clientEp: Endpoint) -> None:
        stub = StubEmitter()
        real = ScrcpyRealBridge(emitter=stub)
        proxy = ScrcpyProxyBridge()
        clientEp.registerBridge(real, asDefault=True)
        mainEp.registerBridge(proxy, asDefault=True)

        await proxy.requestStart()
        await asyncio.sleep(0.15)
        assert stub.started is True

        await proxy.requestStop()
        await asyncio.sleep(0.15)
        assert stub.started is False

    asyncio.run(_withEndpoints(scenario))


def test_real_can_push_metadata_without_initialize() -> None:
    async def scenario(mainEp: Endpoint, clientEp: Endpoint) -> None:
        real = ScrcpyRealBridge()
        proxy = ScrcpyProxyBridge()
        clientEp.registerBridge(real, asDefault=True)
        mainEp.registerBridge(proxy, asDefault=True)

        sc = SCRCPY(serial="push", name="n")
        sc.update(codecId="h265", width=10, height=20)
        await real.send(ScrcpyMetadataMessage(payload=sc))
        await asyncio.wait_for(proxy.metadataEvent.wait(), timeout=2.0)
        assert proxy.lastMetadata is not None
        assert proxy.lastMetadata.codecId == "h265"

    asyncio.run(_withEndpoints(scenario))
