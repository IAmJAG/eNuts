# ==================================================================================
from __future__ import annotations

# ==================================================================================
import importlib
import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from fluxCore.emitters.__outProcessEmitter import OPEmitter


# ==================================================================================
def _ensureTrace() -> None:
    # Do not write `import __monkeyPatch` inside a method: the leading
    # double underscore is name-mangled to _ProbeEmitter__monkeyPatch.
    importlib.import_module("__monkeyPatch")
    from jAGFx.logging import setupLogging
    setupLogging("opemitter")


# ==================================================================================
class ProbeEmitter(OPEmitter):
    """Parent records replies. Child echoes whatever it receives."""

    def __init__(self, serial: str = "probe", name: str | None = "probe") -> None:
        super().__init__(serial=serial, name=name)
        self._side = "parent"
        self.received: list[str] = []

    async def work(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:
        _ensureTrace()
        self._side = "child"
        trace(f"CHILD  work  pid={os.getpid()}")
        await super().work(shutdownEvent, inQueue, outQueue, *args, **kwargs)

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        side = self._side
        try:
            while not shutdownEvent.is_set():
                try:
                    msg = queue.get_nowait()
                except Empty:
                    await asyncWait(0.01)
                    continue

                trace(f"{side.upper():6} recv  {msg!r}  pid={os.getpid()}")

                if side == "child" and self._outQueue is not None:
                    reply = f"echo:{msg}"
                    trace(f"CHILD  send  {reply!r}")
                    self._outQueue.put(reply)
                else:
                    self.received.append(msg)

        finally:
            self._drainQueue(queue)

    def send(self, msg: str) -> None:
        trace(f"PARENT send  {msg!r}  pid={os.getpid()}")
        self._outQueue.put(msg)
