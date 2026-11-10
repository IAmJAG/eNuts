# ==================================================================================
"""Importable probe for OPEmitter message-path tests.

Windows uses the spawn start method. The child process unpickles the
instance, so this class must be importable by module path.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from fluxCore.emitters.__outProcessEmitter import OPEmitter


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
        from jAGFx.logging import setupLogging

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
