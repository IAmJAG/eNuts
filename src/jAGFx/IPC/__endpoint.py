# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Event, Queue as AsyncQueue, Task, create_task, to_thread
from queue import Empty
from typing import TYPE_CHECKING

# ==================================================================================
from ..types.interface.communication import iEndpoint, iIOQueue, iMessage

# ==================================================================================
if TYPE_CHECKING:
    pass


# ==================================================================================
class Endpoint(iEndpoint):
    C_RECEIVE_TIMEOUT: float = 0.01

    def __init__(self, ioQueue: iIOQueue) -> None:
        self._ioQueue: iIOQueue = ioQueue
        self._outbound: AsyncQueue[iMessage] | None = None
        self._inboundTask: Task | None = None
        self._outboundTask: Task | None = None
        self._stopping: Event = Event()
        self._started: bool = False

    @property
    def isStarted(self) -> bool:
        return self._started

    async def start(self) -> None:
        if self._started:
            raise RuntimeError("Endpoint is already started")

        self._stopping.clear()
        self._outbound = AsyncQueue()
        self._inboundTask = create_task(self._pollInbound(), name="Endpoint.inbound")
        self._outboundTask = create_task(self._drainOutbound(), name="Endpoint.outbound")
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return

        self._stopping.set()

        for task in (self._inboundTask, self._outboundTask):
            if task is not None and not task.done():
                task.cancel()

        for task in (self._inboundTask, self._outboundTask):
            if task is not None:
                try:
                    await task
                except CancelledError:
                    pass

        self._inboundTask = None
        self._outboundTask = None
        self._outbound = None
        self._started = False

    async def send(self, message: iMessage) -> None:
        if not self._started or self._outbound is None:
            raise RuntimeError("Endpoint is not started")

        await self._outbound.put(message)

    async def _pollInbound(self) -> None:
        while not self._stopping.is_set():
            try:
                message = await to_thread(
                    self._ioQueue.receive,
                    self.C_RECEIVE_TIMEOUT,
                )
            except Empty:
                continue
            except CancelledError:
                break
            except Exception:
                if self._stopping.is_set():
                    break
                continue

            try:
                await self._onInbound(message)
            except CancelledError:
                break
            except Exception:
                continue

    async def _drainOutbound(self) -> None:
        while not self._stopping.is_set():
            if self._outbound is None:
                break

            try:
                message = await self._outbound.get()
            except CancelledError:
                break

            try:
                await to_thread(self._ioQueue.send, message)
            except CancelledError:
                break
            except Exception:
                if self._stopping.is_set():
                    break
                continue

    async def _onInbound(self, message: iMessage) -> None:
        """Phase 2: receive only. Dispatch is added in Phase 3+."""
        return


# ==================================================================================
__all__ = ["Endpoint"]
