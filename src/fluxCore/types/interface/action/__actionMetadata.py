# ==================================================================================
# src/fluxCore/actions/__action.py
# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
DEVICE_MINIMUM_WAIT: float = 0.01
# ==================================================================================

# ==================================================================================
@runtime_checkable
class iActionMetadata(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def data(self) -> dict: ...
    def delayBefore(self, time: float = None): ...
    def delayAfter(self, time: float = None): ...
    def execute(self) -> Any:
        raise NotImplementedError("Execute method must be implemented by subclasses of Action")
