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
    """Child reads its in-queue and writes echo:<msg> on its out-queue."""

    def __init__(self, serial: str = "probe", name: str | None = "probe") -> None:
        super().__init__(serial=serial, name=name)

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
