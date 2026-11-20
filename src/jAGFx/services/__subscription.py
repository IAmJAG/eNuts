# ==================================================================================
from asyncio import to_thread
from inspect import iscoroutinefunction
from typing import Callable, Dict, List

# ==================================================================================
from ..types.interface.services import iSubscription


# ==================================================================================
class Subscription(iSubscription):
    def __init__(self) -> None:
        self._callbacks: Dict[str, List[Callable]] = {}
        self._suppressEvent = False

    def subscribe(self, event: str, callback: Callable) -> None:
        if event not in self._callbacks:
            self._callbacks[event] = []

        if callback in self._callbacks[event]:
            warning(f"Callback for event '{event}' already exists.")
            return
        
        self._callbacks[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if event in self._callbacks:
            if callback in self._callbacks[event]:
                self._callbacks[event].remove(callback)

            if not self._callbacks[event]:
                del self._callbacks[event]

    def raiseEvent(self, event: str, nonBlocking: bool = False, *args, **kwargs) -> None: 
        if event not in self._callbacks: return
        if self._suppressEvent: return

        async def _asyncRunner(_callback: Callable, *_args, **_kwargs) -> None:
            if nonBlocking:                
                return await to_thread(_callback, *_args, **_kwargs)

            if iscoroutinefunction(callback):
                # createTask is available globally via __monkeyPatch
                return createTask(callback, *args, **kwargs)

            else:
                callback(*args, **kwargs)

        if event in self._callbacks:
            for callback in self._callbacks[event]:
                createTask(_asyncRunner, callback, *args, **kwargs)

    def setSuppressEvent(self, value: bool = True) -> None:
        self._suppressEvent = value

# ==================================================================================
__all__ = ["Subscription"]
