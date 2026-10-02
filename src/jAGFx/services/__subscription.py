# ==================================================================================
from typing import Awaitable, Callable, Dict, List

# ==================================================================================
from ..types.interface.services import iSubscription


# ==================================================================================
class Subscription(iSubscription):
    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = dict[str, List[Callable]]()

    def subscribe(self, event: str, callback: Callable):
        if event not in self._callbacks:
            self._callbacks[event]: List[Callable] = list[Callable]()

        self._callbacks.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        if event in self._callbacks:
            if callback in self._callbacks[event]:
                self._callbacks[event].remove(callback)

        if self._callbacks[event] == []:
            del self._callbacks[event]

    def raiseEvent(self, event: str, *args, **kwargs):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                callback(*args, **kwargs)

# ==================================================================================
class AsyncSubscription(Subscription):
    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = dict[str, List[Callable]]()

    def subscribe(self, event: str, callback: Callable[..., Awaitable]):
        super().subscribe(event, callback)

    def unsubscribe(self, event: str, callback: Callable[..., Awaitable]):
        super().unsubscribe(event, callback)

    def raiseEvent(self, event: str, *args, **kwargs):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                if callable(callback):
                    if isinstance(callback, Awaitable):
                        createTask(callback, *args, **kwargs)

                    else:
                        callback(*args, **kwargs)

                else:
                    raise TypeError(f"Callback for event '{event}' is not callable.")

    async def asyncRaiseEvent(self, event: str, *args, **kwargs):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                if callable(callback):
                    if isinstance(callback, Awaitable):
                        await callback(*args, **kwargs)

                    else:
                        callback(*args, **kwargs)

                else:
                    raise TypeError(f"Callback for event '{event}' is not callable.")