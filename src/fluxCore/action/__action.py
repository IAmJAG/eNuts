# ==================================================================================
# src/fluxCore/action/__action.py
# ==================================================================================
from time import sleep
from typing import Any

# ==================================================================================
from ..types.interface.action.__actionMetadata import iActionMetadata

# ==================================================================================
DEVICE_MINIMUM_WAIT: float = 0.01
# ==================================================================================


# ==================================================================================
class Action(iActionMetadata):
    def __init__(self, name: str, data={}, dbe: float = 0.0, dae: float = 0.0):
        self._name: str = name
        self._data: dict = data
        self._delayBefore: float = dbe
        self._delayAfter: float = dae

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def data(self) -> dict:
        return self._data

    def wait(self, time: float = None):
        if time is None or time == 0:
            time = DEVICE_MINIMUM_WAIT
        sleep(time)

    def delayBefore(self, time: float = None):
        if time is None:
            time = DEVICE_MINIMUM_WAIT
        sleep(time)

    def delayAfter(self, time: float = None):
        if time is None:
            time = DEVICE_MINIMUM_WAIT
        sleep(time)

    async def execute(self) -> Any:
        raise NotImplementedError(
            "Execute method must be implemented by subclasses of Action"
        )
