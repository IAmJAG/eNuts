# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Optional

# ==================================================================================
from jAGFx.services import AsyncService

# ==================================================================================
from ..types.interface.stream.__frameView import iFrameView
from ..types.interface.stream.frameRing import iFrameRing
from ..types.interface.stream.frameRing.slot import iRingSlot

# ==================================================================================
try:
    from shiboken6 import isValid as _qtIsValid
except ImportError:  # pragma: no cover
    def _qtIsValid(obj: Any) -> bool:
        return obj is not None

# ==================================================================================
C_DEFAULT_DISPLAY_FPS: float = 30.0


# ==================================================================================
class Presenter(AsyncService):
    """Latest-frame display consumer; holds a slot lease only while presenting."""

    def __init__(
        self,
        displayFps: float = C_DEFAULT_DISPLAY_FPS,
        name: str | None = None,
    ) -> None:
        if displayFps <= 0.0:
            raise ValueError("displayFps must be greater than zero")
        super().__init__(
            work=self._present,
            name=name or "Presenter",
            throttle=1.0 / displayFps,
        )
        self._ring: Optional[iFrameRing] = None
        self._view: Any = None
        self._lastSequence: Optional[int] = None

    def attachRing(self, ring: iFrameRing) -> None:
        self._ring = ring
        self._lastSequence = None

    def detachRing(self) -> None:
        self._ring = None
        self._lastSequence = None

    def attachView(self, view: iFrameView | Any) -> None:
        self._view = view
        self._lastSequence = None

    def detachView(self) -> None:
        view = self._view
        self._view = None
        self._lastSequence = None
        if view is None:
            return
        clear = getattr(view, "clear", None)
        if callable(clear):
            try:
                clear()
            except Exception as ex:
                warning(f"[Presenter] view.clear failed: {ex}")

    @property
    def displayFps(self) -> float:
        throttle = self.throttle
        return 0.0 if throttle <= 0.0 else 1.0 / throttle

    @displayFps.setter
    def displayFps(self, value: float) -> None:
        if value <= 0.0:
            raise ValueError("displayFps must be greater than zero")
        self.throttle = 1.0 / value

    async def _present(self) -> None:
        ring = self._ring
        view = self._view
        if ring is None or view is None:
            return
        if not _qtIsValid(view):
            self._view = None
            self._lastSequence = None
            return

        slot: Optional[iRingSlot] = ring.latest()
        if slot is None:
            return
        try:
            if slot.sequence == self._lastSequence:
                return
            frame = slot.payload
            if frame is None:
                return
            present = getattr(view, "present", None)
            if not callable(present):
                warning("[Presenter] view lacks present")
                return
            try:
                ok = present(frame)
            except RuntimeError as ex:
                message = str(ex).lower()
                if "already deleted" in message or "internal c++ object" in message:
                    self._view = None
                    self._lastSequence = None
                    return
                raise
            except Exception as ex:
                warning(f"[Presenter] present failed: {ex}")
                return
            if ok is not False:
                self._lastSequence = slot.sequence
        finally:
            ring.release(slot)


# ==================================================================================
__all__ = ["Presenter", "C_DEFAULT_DISPLAY_FPS"]
# ==================================================================================
