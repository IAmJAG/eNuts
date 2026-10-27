# ==================================================================================
"""Minimal serializable payload for IPC smoke tests."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.serializer import Serializable


# ==================================================================================
class SmokePayload(Serializable):
    def __init__(self, text: str = "", kind: str = "SmokePayload") -> None:
        super().__init__()
        self._text: str = text
        self._kind: str = kind
        self.Properties.extend(["text", "kind"])

    @property
    def text(self) -> str:
        return self._text

    @property
    def kind(self) -> str:
        return self._kind


# ==================================================================================
__all__ = ["SmokePayload"]
