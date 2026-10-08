# ==================================================================================
from multiprocessing import Event, Process
from multiprocessing.synchronize import Event as SyncEvent
from typing import Awaitable, Callable

# ==================================================================================
from jAGFx.names import getRandomName
from jAGFx.types.interface.services import iService


# ==================================================================================
class Service(iService):
    def __init__(self, work: Callable[..., Awaitable], name: str | None = None) -> None:        
        self.work: Callable[..., Awaitable] = work
        self._name: str = name or getRandomName()
        self._process: Process | None = None

    @property
    def name(self): return self._name

    async def work(self, shutdownEvent: SyncEvent, *args, **kwargs): ...

    def start(self, *args, **kwargs):
        if self._process is not None and self._process.is_alive(): return

        shutdownEvent: SyncEvent = Event()
        async def work(_shutdownEvent: SyncEvent, *args, **kwargs): ...

        work = self.work
        process = Process(
            target=work, args=(shutdownEvent, *args),
            kwargs=kwargs, daemon=True, name=self._name,
        )
        process.start()        
        self._process = process
    