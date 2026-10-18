# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QObject, Signal, SignalInstance
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QSizePolicy

# ==================================================================================
from jAGQt.widgets.Image import Image
from jAGQt.widgets.page import Page

# ==================================================================================
from .__navigationPages import buildBlankPage


# ==================================================================================
class DeviceFrameBridge(QObject):
    """Marshal decoded frames onto the Qt thread for Image."""

    frameReady: SignalInstance = Signal(object)  # QImage | QPixmap

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)


# ==================================================================================
def buildDevicePage(key: str, title: str, serial: str) -> Page:
    """Device Page with Image stream host (content slot).

    Emitter is **not** owned here — resolve via deviceManager + ensureRunning.
    """
    page = buildBlankPage(key, title, f"Device {serial}")
    view = Image(bg="#1a1a1a", backend="software")
    view.setObjectName("W_DEVICE_STREAM")
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    page.addWidget(view, stretch=1)

    bridge = DeviceFrameBridge(page)
    bridge.frameReady.connect(lambda img: _applyFrame(view, img))

    # Stash for WorkSpace stream attach
    page._deviceSerial = serial  # type: ignore[attr-defined]
    page._streamView = view  # type: ignore[attr-defined]
    page._frameBridge = bridge  # type: ignore[attr-defined]
    page._streamAttached = False  # type: ignore[attr-defined]

    verbose(f"[pages] device page key={key!r} serial={serial!r}")
    return page


def _applyFrame(view: Image, img: object) -> None:
    try:
        if isinstance(img, QImage):
            view.image = img
        elif isinstance(img, QPixmap):
            view.image = img
        else:
            return
    except Exception as ex:
        warning(f"[pages] applyFrame failed: {ex}")
