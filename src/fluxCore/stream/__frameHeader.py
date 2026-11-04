# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic_ns
from typing import Optional

# ==================================================================================
from .__eDecodeFormat import eDecodeFormat
from .__frameFlags import FrameFlags


# ==================================================================================
class FrameHeader:
    __slots__ = ("_sequence", "_pts", "_width", "_height", "_format", "_format")
    def __init__(
        self, pts: int, width: int, height: int, sequence: Optional[int] = None,
        format: eDecodeFormat = eDecodeFormat.PIL, flags: FrameFlags = FrameFlags.NONE
    ) -> None:
        sequence: int = monotonic_ns() if sequence is None else sequence
        self._sequence: int = sequence
        self._pts: int = pts
        self._width: int = width
        self._height: int = height
        self._format: eDecodeFormat = format
        self._flags: FrameFlags = flags

    @property
    def sequence(self) -> int: 
        return self._sequence
    
    @property
    def pts(self) -> int: 
        return self._pts

    @property
    def width(self) -> int: 
        return self._width

    @property
    def height(self) -> int: 
        return self._height

    @property
    def format(self) -> eDecodeFormat: 
        return self._format

    @property
    def flags(self) -> FrameFlags: 
        return self._flags


__all__ = ["FrameHeader"]