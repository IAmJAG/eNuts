# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from fluxCore.emitters.__outProcessEmitter import outOfProcessEmitter
from .echoWorker import echoWorker


# ==================================================================================
class ProbeEmitter(outOfProcessEmitter):
    """Uses the module-level echo worker. Records the shared inbound."""

    def __init__(self, serial: str = "probe", name: str | None = "probe") -> None:
        super().__init__(serial=serial, name=name, worker=echoWorker)
        self.received: list[str] = []

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        try:
            while not shutdownEvent.is_set():
                try:
                    msg = await to_thread(queue.get, True, 0.1)

                except Empty:
                    continue

                self.received.append(msg)
                trace(f"FLOW  parent inbound got {msg!r}  n={len(self.received)}")

        finally:
            return
