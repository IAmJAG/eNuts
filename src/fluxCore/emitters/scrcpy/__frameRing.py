# ==================================================================================
"""In-process ring of slot headers + opaque GPU/CPU handles.

Does not move pixels over IPC. Producer publishes headers; main reads newest ready.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from threading import Lock
from typing import Any

# ==================================================================================
from .__frameSlot import (
    C_DEFAULT_RING_SIZE,
    FramePresentFormat,
    FrameSlotFlags,
    FrameSlotHeader,
    clampRingSize,
    makeFrameSlotHeader,
    pickWriteIndex,
)


# ==================================================================================
class FrameRing:
    """Fixed-size ring: header per slot + optional opaque handle/payload."""

    def __init__(self, ringSize: int = C_DEFAULT_RING_SIZE) -> None:
        self._n = clampRingSize(ringSize)
        self._lock = Lock()
        self._headers: list[FrameSlotHeader | None] = [None] * self._n
        self._payloads: list[Any] = [None] * self._n
        self._displayIndex: int = 0
        self._writeCursor: int = 0
        self._publishedSeq: int = 0
        self._readyIndex: int | None = None

    @property
    def ringSize(self) -> int:
        return self._n

    @property
    def publishedSeq(self) -> int:
        with self._lock:
            return self._publishedSeq

    def setDisplayIndex(self, index: int) -> None:
        with self._lock:
            self._displayIndex = int(index) % self._n

    def publish(
        self,
        *,
        width: int,
        height: int,
        pts: int = 0,
        format: FramePresentFormat | int = FramePresentFormat.RGBA8,
        flags: FrameSlotFlags | int = FrameSlotFlags.NONE,
        payload: Any = None,
        stride: int = 0,
    ) -> FrameSlotHeader:
        with self._lock:
            idx = pickWriteIndex(
                displayIndex=self._displayIndex,
                ringSize=self._n,
                preferred=self._writeCursor,
            )
            self._publishedSeq += 1
            hdr = makeFrameSlotHeader(
                seq=self._publishedSeq,
                pts=pts,
                width=width,
                height=height,
                stride=stride,
                format=format,
                flags=flags,
            )
            self._headers[idx] = hdr
            self._payloads[idx] = payload
            self._readyIndex = idx
            self._writeCursor = (idx + 1) % self._n
            return hdr

    def latest(self) -> tuple[FrameSlotHeader, Any] | None:
        with self._lock:
            if self._readyIndex is None:
                return None
            hdr = self._headers[self._readyIndex]
            if hdr is None:
                return None
            return hdr, self._payloads[self._readyIndex]

    def acquireForDisplay(self) -> tuple[int, FrameSlotHeader, Any] | None:
        """Mark latest ready as display slot; returns index, header, payload."""
        with self._lock:
            if self._readyIndex is None:
                return None
            idx = self._readyIndex
            hdr = self._headers[idx]
            if hdr is None:
                return None
            self._displayIndex = idx
            return idx, hdr, self._payloads[idx]


# ==================================================================================
__all__ = ["FrameRing"]
