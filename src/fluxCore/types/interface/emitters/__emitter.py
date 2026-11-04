# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.services import iService, iSubscription

# ==================================================================================
from ..device import iDevice


# ==================================================================================
@runtime_checkable
class iEmitter(iService, iSubscription, iDevice, Protocol):
    @classmethod
    def toDevice(self, device: iDevice) -> Optional[iDevice]: ...