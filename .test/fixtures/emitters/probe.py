# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from fluxCore.emitters.__outProcessEmitter import OPEmitter


# ==================================================================================
class ProbeEmitter(OPEmitter):
    """Child echoes. Parent receiver records what comes back.

    parent._outQueue == child inQueue
    parent._inQueue  == child outQueue

    start() launches the parent receiver on _inQueue. If the test also
    reads that queue, the receiver wins the race and the test sees nothing.
    """

    def __init__(self, serial: str = "probe", name: str | None = "probe") -> None:
        super().__init__(serial=serial, name=name)
        self.received: list[str] = []

    async def work(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:
        print("CHILD up", flush=True)
        try:
            while not shutdownEvent.is_set():
                try:
                    msg = inQueue.get_nowait()
                except Empty:
                    await asyncio.sleep(0.01)
                    continue
                print(f"CHILD got {msg!r}", flush=True)
                outQueue.put(f"echo:{msg}")
        finally:
            print("CHILD down", flush=True)

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        # Parent side only. Child work() does not start this.
        try:
            while not shutdownEvent.is_set():
                try:
                    msg = queue.get_nowait()
                except Empty:
                    await asyncio.sleep(0.01)
                    continue
                print(f"PARENT got {msg!r}", flush=True)
                self.received.append(msg)
        finally:
            self._drainQueue(queue)
