# ==================================================================================
"""Device stream abstraction for KG Recorder / Playback surfaces."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Callable, Optional, Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QObject, Signal, SignalInstance
from PySide6.QtGui import QImage

# ==================================================================================
from fluxCore.emitters.scrcpy import FrameRing, FrameSlotFlags, shouldSkipPresent

# ==================================================================================
C_ON_FRAME = "ON_FRAME"


# ==================================================================================
@runtime_checkable
class iDeviceStream(Protocol):
    async def ensureRunning(self, serial: str) -> None: ...
    def attachView(self, view: Any) -> None: ...
    def detachView(self) -> None: ...
    def stop(self) -> None: ...


# ==================================================================================
class StreamFrameBridge(QObject):
    """Qt-thread marshal for stream presents."""

    frameReady: SignalInstance = Signal(object, object)  # header-like dict, QImage|None

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)


# ==================================================================================
class LocalDeviceStream:
    """In-process stream: deviceManager emitter → FrameRing → GLImage.presentExternal.

    Transitional pixel path uses QImage from existing decode. GPU-handle path is
    reserved on presentExternal(handle=...).
    """

    def __init__(self, deviceManager: Any) -> None:
        self._mgr = deviceManager
        self._view: Any = None
        self._serial: str | None = None
        self._handler: Callable | None = None
        self._ring = FrameRing()
        self._bridge = StreamFrameBridge()
        self._lastSeq: int | None = None
        self._bridge.frameReady.connect(self._onQtFrame)

    def attachView(self, view: Any) -> None:
        self._view = view

    def detachView(self) -> None:
        self.stop()
        self._view = None

    def stop(self) -> None:
        serial = self._serial
        handler = self._handler
        if serial and handler and self._mgr is not None:
            emitter = self._mgr.getEmitter(serial)
            if emitter is not None:
                try:
                    emitter.unsubscribe(C_ON_FRAME, handler)
                except Exception:
                    pass
        self._handler = None
        self._serial = None
        view = self._view
        if view is not None and hasattr(view, "clearPresent"):
            try:
                view.clearPresent()
            except Exception:
                pass

    async def ensureRunning(self, serial: str) -> None:
        if not serial:
            return
        if self._serial == serial and self._handler is not None:
            return
        self.stop()
        self._serial = serial
        emitter = await self._mgr.ensureRunning(serial)

        def _onFrame(frame: object) -> None:
            try:
                if getattr(frame, "isConfig", False):
                    return
                qimg = self._frameToQImage(frame, emitter)
                if qimg is None:
                    return
                hdr = self._ring.publish(
                    width=qimg.width(),
                    height=qimg.height(),
                    pts=int(getattr(frame, "pts", 0) or 0),
                    flags=FrameSlotFlags.NONE,
                    payload=qimg,
                )
                self._bridge.frameReady.emit(
                    {"seq": hdr.seq, "pts": hdr.pts, "w": hdr.width, "h": hdr.height},
                    qimg,
                )
            except Exception:
                pass

        emitter.subscribe(C_ON_FRAME, _onFrame)
        self._handler = _onFrame

    def _onQtFrame(self, meta: object, image: object) -> None:
        view = self._view
        if view is None or not hasattr(view, "presentExternal"):
            return
        if not isinstance(meta, dict):
            return
        seq = int(meta.get("seq", 0))
        if shouldSkipPresent(slotSeq=seq, lastPresentedSeq=self._lastSeq):
            return
        ok = view.presentExternal(
            seq=seq,
            width=int(meta.get("w", 0)),
            height=int(meta.get("h", 0)),
            pts=int(meta.get("pts", 0)),
            image=image if isinstance(image, QImage) else None,
        )
        if ok:
            self._lastSeq = seq
            acq = self._ring.acquireForDisplay()
            if acq is not None:
                idx, _hdr, _ = acq
                self._ring.setDisplayIndex(idx)

    @staticmethod
    def _frameToQImage(frame: object, emitter: object) -> Optional[QImage]:
        try:
            decode = getattr(frame, "decode", None)
            if decode is None:
                return None
            codec = getattr(emitter, "_codecContext", None)
            if codec is None:
                return None
            vf = decode(codec, toGPU=False)
            if vf is None:
                return None
            if hasattr(vf, "to_ndarray"):
                import numpy as np

                arr = vf.to_ndarray(format="rgb24")
                if not isinstance(arr, np.ndarray):
                    return None
                h, w, _c = arr.shape
                qimg = QImage(arr.data, w, h, 3 * w, QImage.Format.Format_RGB888)
                return qimg.copy()
            if hasattr(vf, "to_image"):
                pil = vf.to_image()
                data = pil.convert("RGB").tobytes()
                w, h = pil.size
                qimg = QImage(data, w, h, 3 * w, QImage.Format.Format_RGB888)
                return qimg.copy()
        except Exception:
            return None
        return None


# ==================================================================================
class IpcDeviceStream:
    """Cross-process stream consumer — blocked on GPU handle interop (see plan).

    Raises NotImplementedError until platform importer + worker export handles.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "IpcDeviceStream requires cross-process GPU interop (DMABUF/shared "
            "texture). FrameSlotHeader + FrameRing are ready; implement platform "
            "importer before enabling IPC stream mode."
        )


# ==================================================================================
__all__ = [
    "iDeviceStream",
    "LocalDeviceStream",
    "IpcDeviceStream",
    "StreamFrameBridge",
]
