# ==================================================================================
from typing import Callable, Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iSubscription(Protocol):
    def subscribe(self, event: str, callback: Callable): ...
    def unsubscribe(self, event: str, callback: Callable): ...
