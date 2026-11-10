# ==================================================================================
"""Smoke: OPEmitter message path, end to end, with trace hops.

Queue wiring (parent perspective):

    parent._outQueue  ==  child inQueue     parent → child
    parent._inQueue   ==  child outQueue    child  → parent

Hops logged with trace():

    1. PARENT send     put on parent._outQueue
    2. CHILD  receive  _receiver pulls from child inQueue
    3. CHILD  reply    put on child outQueue
    4. PARENT receive  _receiver pulls from parent._inQueue
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
import os
from pathlib import Path
import sys

# ==================================================================================
_REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

import __monkeyPatch  # noqa: E402, F401  — installs trace as a builtin
from jAGFx.logging import setupLogging  # noqa: E402
from fluxCore.emitters.__outProcessEmitter import OPEmitter  # noqa: E402
from multiprocessing.synchronize import Event as syncEvent  # noqa: E402
from multiprocessing import Queue  # noqa: E402
from queue import Empty  # noqa: E402


# ==================================================================================
class ProbeEmitter(OPEmitter):
    """Records the parent-side receive path and echoes from the child."""

    def __init__(self, serial: str = "probe", name: str | None = "probe") -> None:
        super().__init__(serial=serial, name=name)
        self._side: str = "parent"
        self.received: list[str] = []

    def start(self, *args, **kwargs) -> None:
        self._side = "parent"
        trace(f"[PARENT pid={os.getpid()}] start")
        super().start(*args, **kwargs)
        trace(
            f"[PARENT] queues ready "
            f"out(parent→child)={id(self._outQueue)} "
            f"in(child→parent)={id(self._inQueue)}"
        )

    async def work(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:
        # Child is a fresh process: install builtins and a console logger.
        import __monkeyPatch  # noqa: F401
        setupLogging("opemitter-child")

        self._side = "child"
        trace(
            f"[CHILD  pid={os.getpid()}] work entered "
            f"in(from parent)={id(inQueue)} out(to parent)={id(outQueue)}"
        )
        await super().work(shutdownEvent, inQueue, outQueue, *args, **kwargs)
        trace(f"[CHILD  pid={os.getpid()}] work exiting")

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        side = self._side
        trace(f"[{side.upper():6} pid={os.getpid()}] receiver loop start")
        try:
            while not shutdownEvent.is_set():
                try:
                    msg = queue.get_nowait()
                except Empty:
                    await asyncWait(0.01)
                    continue

                trace(f"[{side.upper():6} pid={os.getpid()}] received {msg!r}")

                if side == "child":
                    reply = f"echo:{msg}"
                    trace(f"[CHILD  pid={os.getpid()}] reply {reply!r} → outQueue")
                    if self._outQueue is not None:
                        self._outQueue.put(reply)
                else:
                    self.received.append(msg)
                    trace(f"[PARENT pid={os.getpid()}] stored {msg!r} (n={len(self.received)})")

        finally:
            self._drainQueue(queue)
            trace(f"[{side.upper():6} pid={os.getpid()}] receiver drained")

    def sendToChild(self, msg: str) -> None:
        trace(f"[PARENT pid={os.getpid()}] send {msg!r} → outQueue")
        if self._outQueue is None:
            raise RuntimeError("not started")
        self._outQueue.put(msg)


# ==================================================================================
async def _roundtrip() -> None:
    setupLogging("opemitter-parent")
    emitter = ProbeEmitter()

    emitter.start()
    try:
        emitter.sendToChild("ping")

        # Parent receiver is polled; give the child time to echo.
        for _ in range(50):
            if emitter.received:
                break
            await asyncWait(0.05)

        assert emitter.received == ["echo:ping"], emitter.received
        trace(f"[PARENT] roundtrip ok: {emitter.received}")

    finally:
        await emitter.stopAsync(timeout=2.0)
        trace("[PARENT] stopped")


def test_opemitter_message_roundtrip() -> None:
    asyncio.run(_roundtrip())
