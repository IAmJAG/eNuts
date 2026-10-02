# ==================================================================================
from __future__ import annotations

# ==================================================================================
from json import dumps, loads
from multiprocessing import Queue
from queue import Empty
from typing import Any, Dict

# ==================================================================================
from ..serializer import jsonDecode as dictDecode
from ..types.interface.communication import iIOQueue, iMessage


# ==================================================================================
class IOQueue(iIOQueue):
    def __init__(self, outboundQueue: Queue, inboundQueue: Queue) -> None:
        self._in: Queue = inboundQueue
        self._ou: Queue = outboundQueue

    @classmethod
    def createPair(cls) -> tuple[IOQueue, IOQueue]:
        queueA, queueB = Queue(), Queue()
        return (cls(queueA, queueB), cls(queueB, queueA))

    def send(self, message: iMessage) -> None:
        dictMsg: Dict = message.encode()
        jsonMsg: str = dumps(dictMsg) 
        self._ou.put(jsonMsg)

    def receive(self, timeout: float | None = None) -> Any:
        timeout = timeout if timeout is not None else 0.01
        jsonMsg: str = self._in.get(timeout=timeout)
        dictMsg: Dict = loads(jsonMsg)
        return dictDecode(dictMsg)

    def close(self) -> None:
        try:
            self._ou.close()
            self._in.close()

        except Exception:
            pass

    def cancelJoinThread(self) -> None:
        try:
            self._in.cancel_join_thread()
            self._ou.cancel_join_thread()

        except Exception:
            pass


# ==================================================================================
__all__ = ["IOQueue"]
