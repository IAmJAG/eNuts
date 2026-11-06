# ==================================================================================
from __future__ import annotations

from typing import Any, Optional

# ==================================================================================
from PySide6.QtCore import QObject, Signal, SignalInstance

# ==================================================================================
from .__streamHelpers import shouldSkipPresent

# ==================================================================================
try:
    from shiboken6 import isValid as _qtIsValid
except ImportError:  # pragma: no cover
    def _qtIsValid(obj: Any) -> bool:  # type: ignore[misc]
        return obj is not None


# ==================================================================================
class StreamPresenter(QObject):
    """Queues frameReady from emitter thread to GUI thread and calls view.presentExternal."""

    frameReady: SignalInstance = Signal(object, object)  # (meta: dict, image: QImage)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._lastSeq: Optional[int] = None

    def present(self, view: Any, meta: dict, image: Any) -> None:
        """Guard + present on the GUI thread."""
        if view is None:
            return

        # View may outlive C++ after page teardown / stack hide.
        if not _qtIsValid(view):
            return

        if not hasattr(view, "presentExternal"):
            warning("[StreamPresenter] present: view lacks presentExternal")
            return

        if not isinstance(meta, dict):
            warning("[StreamPresenter] present: meta is not a dict")
            return

        if image is None or getattr(image, "isNull", lambda: True)():
            return

        seq = int(meta.get("seq", 0))
        if shouldSkipPresent(slotSeq=seq, lastPresentedSeq=self._lastSeq):
            return

        try:
            ok = view.presentExternal(
                seq=seq,
                width=int(meta.get("w", 0)) or getattr(image, "width", lambda: 0)(),
                height=int(meta.get("h", 0)) or getattr(image, "height", lambda: 0)(),
                pts=int(meta.get("pts", 0)),
                image=image,
            )
        except RuntimeError as ex:
            # libshiboken: Internal C++ object already deleted
            if "already deleted" in str(ex).lower() or "internal c++ object" in str(ex).lower():
                return
            raise
        if ok:
            self._lastSeq = seq


__all__ = ["StreamPresenter"]
