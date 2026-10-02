# ==================================================================================
from asyncio import iscoroutinefunction
from typing import Awaitable, Callable, Dict, List

# ==================================================================================
from ..types.interface.services import iSubscription


# ==================================================================================
class Subscription(iSubscription):
    def __init__(self) -> None:
        self._callbacks: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable) -> None:
        self._callbacks.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if event in self._callbacks:
            if callback in self._callbacks[event]:
                self._callbacks[event].remove(callback)
            if not self._callbacks[event]:
                del self._callbacks[event]

    def raiseEvent(self, event: str, *args, **kwargs) -> None:
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                callback(*args, **kwargs)


# ==================================================================================
class AsyncSubscription(Subscription):
    def __init__(self) -> None:
        super().__init__()

    def subscribe(self, event: str, callback: Callable[..., Awaitable]) -> None:
        super().subscribe(event, callback)

    def unsubscribe(self, event: str, callback: Callable[..., Awaitable]) -> None:
        super().unsubscribe(event, callback)

    def raiseEvent(self, event: str, *args, **kwargs) -> None:
        if event not in self._callbacks:
            return

        for callback in self._callbacks[event]:
            if not callable(callback):
                raise TypeError(f"Callback for event '{event}' is not callable.")

            if iscoroutinefunction(callback):
                # createTask is available globally via __monkeyPatch
                createTask(callback, *args, **kwargs)
            else:
                callback(*args, **kwargs)

    async def asyncRaiseEvent(self, event: str, *args, **kwargs) -> None:
        if event not in self._callbacks:
            return

        for callback in self._callbacks[event]:
            if not callable(callback):
                raise TypeError(f"Callback for event '{event}' is not callable.")

            if iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)


# ==================================================================================
__all__ = ["Subscription", "AsyncSubscription"]
