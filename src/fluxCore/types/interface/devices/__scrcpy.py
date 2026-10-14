# ==================================================================================
# src/fluxCore/types/interface/__scrcpy.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..device import iDevice


# ==================================================================================
@runtime_checkable
class iSCRCPY(iDevice, Protocol):
    @property
    def codecId(self) -> str: ...
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...