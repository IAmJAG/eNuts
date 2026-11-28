# ==================================================================================
from collections.abc import Callable
from inspect import iscoroutinefunction

# ==================================================================================
from ..types.interface.services import iSubscription


# ==================================================================================
class Subscription(iSubscription):
    def __init__(self) -> None:
        super().__init__()
        self._callbacks: dict[str, list[Callable]] = {}
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

    def raiseEvent(self, event: str, *args, **kwargs) -> None: 
        if event not in self._callbacks: return
        if self._suppressEvent: return

        async def _asyncRunner(_callback: Callable, *_args, **_kwargs) -> None:
            if iscoroutinefunction(_callback):
                # createTask is available globally via __monkeyPatch
                return createTask(callback, *args, **kwargs)

            else:
                _callback(*args, **kwargs)

        if event in self._callbacks:
            for callback in self._callbacks[event]:
                createTask(_asyncRunner, callback, *args, **kwargs)

    def setSuppressEvent(self, value: bool = True) -> None:
        self._suppressEvent = value

# ==================================================================================
__all__ = ["Subscription"]
