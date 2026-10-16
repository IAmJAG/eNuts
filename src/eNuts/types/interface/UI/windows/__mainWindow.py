# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event as asyncEvent

# ==================================================================================
from typing import Optional, Protocol

# ==================================================================================
from jAGQt.types.interface.window import iWindowBase

# ==================================================================================
from .....types.interface.configuration import iENUTSConfiguration


# ==================================================================================
class iENUTSWindow(iWindowBase):
    # Cooperative passthrough — do not use a bare "..." body or the MRO
    # never reaches QMainWindow and Shiboken raises at first Qt call.
    def __init__(
        self, cfg: Optional[iENUTSConfiguration] = None, *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

    @property
    def config(self) -> iENUTSConfiguration: ...
