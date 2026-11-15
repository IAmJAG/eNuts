# ==================================================================================
from __future__ import annotations

from asyncio import sleep as asyncSleep

# ==================================================================================
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from adbutils import AdbDevice, adb


# ==================================================================================
async def DeviceWatcher(
    clientId: str, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue,
    *args, **kwargs,
):
    outQueue.put("SCRCPY")

    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set
    while not isShuttingdown():
        try:
            msg = inQueue.get_nowait()

        except Empty:
            await asyncSleep(0.01)
            continue

        print(f"[{clientId}] {msg}")