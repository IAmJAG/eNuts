# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from av import InvalidDataError, VideoCodecContext, VideoFrame
from PySide6.QtGui import QImage, QPixmap

# ==================================================================================
from fluxCore.action.android.enums import eKeyCode
from fluxCore.deviceInput import AndroidScrcpyInputAdapter
from fluxCore.types.interface.deviceInput import iDeviceInputAdapter
from fluxCore.types.interface.packets import iFrame

# ==================================================================================
from ..UI.widgets.streamer import imageStreamer
from .__qtKeyMap import MapQtKeyToAndroid, MapQtModifiersToMeta


# ==================================================================================
class StreamPipeline:
    """Bind a live device session to imageStreamer (frames + input).

    Frame path: ON_FRAME → decode → SetStreamingImage.
    Input path: streamer signals → image→device map + Qt→Android → adapter.
    """

    def __init__(
        self,
        streamer: imageStreamer,
        adapter: iDeviceInputAdapter | None = None,
    ) -> None:
        self._streamer: imageStreamer = streamer
        self._adapter: iDeviceInputAdapter = adapter or AndroidScrcpyInputAdapter()
        self._decoder: Optional[VideoCodecContext] = None
        self._deviceWidth: int = 0
        self._deviceHeight: int = 0
        self._imageWidth: int = 0
        self._imageHeight: int = 0
        self._bound: bool = False

    @property
    def Adapter(self) -> iDeviceInputAdapter:
        return self._adapter

    # ==================================================================================
    def Bind(self, device) -> None:
        """Attach adapter and wire streamer signals. Caller owns emitter subscribe."""
        self.Unbind()
        self._adapter.Attach(device)
        self._decoder = getattr(device, "CodecContext", None)
        self._deviceWidth = int(getattr(device, "width", 0) or 0)
        self._deviceHeight = int(getattr(device, "height", 0) or 0)

        s = self._streamer
        s.TouchPressed.connect(self._onTouchPressed)
        s.TouchMoved.connect(self._onTouchMoved)
        s.TouchReleased.connect(self._onTouchReleased)
        s.WheelScrolled.connect(self._onWheelScrolled)
        s.KeyPressed.connect(self._onKeyPressed)
        s.KeyReleased.connect(self._onKeyReleased)
        s.RightClicked.connect(self._onRightClicked)
        self._bound = True

    def Unbind(self) -> None:
        if not self._bound:
            self._adapter.Detach()
            self._decoder = None
            return
        s = self._streamer
        for lSignal, lSlot in (
            (s.TouchPressed, self._onTouchPressed),
            (s.TouchMoved, self._onTouchMoved),
            (s.TouchReleased, self._onTouchReleased),
            (s.WheelScrolled, self._onWheelScrolled),
            (s.KeyPressed, self._onKeyPressed),
            (s.KeyReleased, self._onKeyReleased),
            (s.RightClicked, self._onRightClicked),
        ):
            try:
                lSignal.disconnect(lSlot)
            except Exception:
                pass
        self._adapter.Detach()
        self._decoder = None
        self._bound = False

    # ==================================================================================
    def OnFrame(self, frame: iFrame) -> None:
        if self._decoder is None:
            return
        try:
            lDecoded: VideoFrame | None = frame.decode(self._decoder, toGPU=False)
        except InvalidDataError:
            return
        except Exception as ex:
            error(f"[{self.__class__.__name__}] decode failed", ex)
            return

        if lDecoded is None:
            return

        try:
            lArr = lDecoded.to_ndarray(format="rgb24")
            lH, lW, _ = lArr.shape
            lBytes = lArr.tobytes()
            lQImage = QImage(
                lBytes, lW, lH, lW * 3, QImage.Format.Format_RGB888
            ).copy()
        except Exception as ex:
            error(f"[{self.__class__.__name__}] frame convert failed", ex)
            return

        self._imageWidth = lW
        self._imageHeight = lH
        if self._deviceWidth <= 0 or self._deviceHeight <= 0:
            self._deviceWidth = lW
            self._deviceHeight = lH

        self._streamer.SetStreamingImage(QPixmap.fromImage(lQImage))

    # ==================================================================================
    def _mapToDevice(self, imgX: float, imgY: float) -> tuple[int, int] | None:
        if self._deviceWidth <= 0 or self._deviceHeight <= 0:
            return None
        lImgW = float(self._imageWidth) if self._imageWidth > 0 else float(self._deviceWidth)
        lImgH = float(self._imageHeight) if self._imageHeight > 0 else float(self._deviceHeight)
        if lImgW <= 0 or lImgH <= 0:
            return None
        lDevX = int(imgX / lImgW * self._deviceWidth)
        lDevY = int(imgY / lImgH * self._deviceHeight)
        lDevX = max(0, min(lDevX, self._deviceWidth - 1))
        lDevY = max(0, min(lDevY, self._deviceHeight - 1))
        return lDevX, lDevY

    def _onTouchPressed(self, x: float, y: float) -> None:
        lMapped = self._mapToDevice(x, y)
        if lMapped is not None:
            self._adapter.TouchDown(lMapped[0], lMapped[1])

    def _onTouchMoved(self, x: float, y: float) -> None:
        lMapped = self._mapToDevice(x, y)
        if lMapped is not None:
            self._adapter.TouchMove(lMapped[0], lMapped[1])

    def _onTouchReleased(self, x: float, y: float) -> None:
        lMapped = self._mapToDevice(x, y)
        if lMapped is not None:
            self._adapter.TouchUp(lMapped[0], lMapped[1])

    def _onWheelScrolled(self, x: float, y: float, h: float, v: float) -> None:
        lMapped = self._mapToDevice(x, y)
        if lMapped is not None:
            self._adapter.Scroll(lMapped[0], lMapped[1], h, v)

    def _onKeyPressed(self, key: int, modifiers: int) -> None:
        lCode = MapQtKeyToAndroid(key)
        if lCode is None:
            return
        self._adapter.KeyDown(lCode, MapQtModifiersToMeta(modifiers))

    def _onKeyReleased(self, key: int, modifiers: int) -> None:
        lCode = MapQtKeyToAndroid(key)
        if lCode is None:
            return
        self._adapter.KeyUp(lCode, MapQtModifiersToMeta(modifiers))

    def _onRightClicked(self, x: float, y: float) -> None:
        self._adapter.KeyDown(eKeyCode.KEYCODE_BACK)
        self._adapter.KeyUp(eKeyCode.KEYCODE_BACK)
