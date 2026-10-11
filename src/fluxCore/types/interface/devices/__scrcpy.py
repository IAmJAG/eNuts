# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..device import iDevice


# ==================================================================================
@runtime_checkable
class iSCRCPY(iDevice, Protocol):
    @property
    def serial(self) -> str: ...
    @property
    def model(self) -> str: ...
    @property
    def manufacturer(self) -> str: ...