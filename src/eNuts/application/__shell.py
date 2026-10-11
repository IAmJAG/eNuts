# ==================================================================================
from __future__ import annotations

from asyncio import Event

# ==================================================================================
from typing import Dict

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
from .__deviceManager import deviceManager


# ==================================================================================
class Shell(iShell):
    def _aInitialize(self):
        shutdownEvent: Event = self._shutdownEvent
        self._devices: Dict[str, iDevice] = deviceManager(shutdownEvent)