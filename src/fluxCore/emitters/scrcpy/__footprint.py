# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.serializer import Serializable


# ==================================================================================
class SCRCPYErrorFootprint(Serializable):
    """Serializable error snapshot for ON_ERROR (never pass the emitter instance)."""

    def __init__(
        self,
        phase: str = "",
        message: str = "",
        serial: str | None = None,
    ) -> None:
        super().__init__()
        self._phase: str = phase
        self._message: str = message
        self._serial: str | None = serial
        self.Properties.extend(["phase", "message", "serial"])

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def message(self) -> str:
        return self._message

    @property
    def serial(self) -> str | None:
        return self._serial


# ==================================================================================
__all__ = ["SCRCPYErrorFootprint"]
