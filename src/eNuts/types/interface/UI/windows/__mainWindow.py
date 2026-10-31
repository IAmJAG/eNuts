# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event as asyncEvent

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================
from jAGQt.types.interface.window import iWindowBase

# ==================================================================================
from .....types.interface.configuration import iENUTSConfiguration


# ==================================================================================
class iENUTSWindow(iWindowBase):
    @property
    def config(self) -> iENUTSConfiguration: ...
