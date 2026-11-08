# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Optional

# ==================================================================================
from jAGFx.services import AsyncService

# ==================================================================================
from ..types.interface.stream.__frameView import iFrameView
from ..types.interface.stream.frameRing import iFrameRing

# ==================================================================================
try:
    from shiboken6 import isValid as _qtIsValid
except ImportError:  # pragma: no cover
    def _qtIsValid(obj: Any) -> bool:  # type: ignore[misc]
        return obj is not None

# ==================================================================================
C_DEFAULT_DISPLAY_FPS: float = 30.0
# ==================================================================================


# ==================================================================================
class Presenter(AsyncService):
    """Display consumer: pulls ``latest`` from a ring and hands frames to an ``iFrameView``.

    Satisfies ``iFrameConsumer`` (``iService`` + ``attachRing`` / ``detachRing``).
    View attach is Presenter-owned and is not part of ``iFrameConsumer``.

    Convert, resize, and paint live on the view. Timing and skip policy live here.
    """

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
        self._lastDataPtr: Optional[int] = None

    # -------------------------------------------------------------------------
    # iFrameConsumer — ring
    # -------------------------------------------------------------------------
    def attachRing(self, ring: iFrameRing) -> None:
        self._ring = ring
        self._lastDataPtr = None

    def detachRing(self) -> None:
        self._ring = None
        self._lastDataPtr = None

    # -------------------------------------------------------------------------
    # Presenter-owned — view (not on iFrameConsumer)
    # -------------------------------------------------------------------------
    def attachView(self, view: iFrameView | Any) -> None:
        self._view = view
        self._lastDataPtr = None

    def detachView(self) -> None:
        view = self._view
        self._view = None
        self._lastDataPtr = None
        if view is None:
            return
        clear = getattr(view, "clear", None)
        if callable(clear):
            try:
                clear()
            except Exception as ex:
                warning(f"[Presenter] view.clear failed: {ex}")

    # -------------------------------------------------------------------------
    # display rate
    # -------------------------------------------------------------------------
    @property
    def displayFps(self) -> float:
        t = self.throttle
        if t <= 0.0:
            return 0.0
        return 1.0 / t

    @displayFps.setter
    def displayFps(self, value: float) -> None:
        if value <= 0.0:
            raise ValueError("displayFps must be greater than zero")
        self.throttle = 1.0 / value

    # -------------------------------------------------------------------------
    # work loop
    # -------------------------------------------------------------------------
    async def _present(self) -> None:
        ring = self._ring
        view = self._view
        if ring is None or view is None:
            return

        if not _qtIsValid(view):
            self._view = None
            self._lastDataPtr = None
            return

        frame = ring.latest()
        if frame is None:
            return

        # Skip if the underlying storage is unchanged since last successful present.
        dataPtr: Optional[int] = None
        try:
            dataPtr = int(frame.data_ptr())  # type: ignore[attr-defined]
        except Exception:
            dataPtr = None

        if dataPtr is not None and dataPtr == self._lastDataPtr:
            return

        present = getattr(view, "present", None)
        if not callable(present):
            warning("[Presenter] view lacks present")
            return

        try:
            ok = present(frame)
        except RuntimeError as ex:
            msg = str(ex).lower()
            if "already deleted" in msg or "internal c++ object" in msg:
                self._view = None
                self._lastDataPtr = None
                return
            raise
        except Exception as ex:
            warning(f"[Presenter] present failed: {ex}")
            return

        if ok is False:
            return

        if dataPtr is not None:
            self._lastDataPtr = dataPtr


# ==================================================================================
__all__ = ["Presenter", "C_DEFAULT_DISPLAY_FPS"]
# ==================================================================================
