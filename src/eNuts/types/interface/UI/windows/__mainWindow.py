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
    def __init__(
        self, cfg: Optional[iENUTSConfiguration] = None, *args, **kwargs,
    ) -> None: ...

    @property
    def config(self) -> iENUTSConfiguration: ...
