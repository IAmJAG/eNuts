# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Type, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QSizePolicy, QWidget

# ==================================================================================
from jAGQt.widgets import CanvasBase, GLCanvas
from jAGQt.widgets.page import Page


# ==================================================================================
class PlaybackBase(Page):
    """Page with a single expanding GLCanvas stream host.

    Subclasses that build a custom content row (e.g. stream + side strip) should
    call ``Page._wInitializeUI`` themselves and must not rely on this default
    stream insert.
    """

    def __init__(
        self, title: str, description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        commandBarOn: bool = False, id: Optional[str] = None, *args, **kwargs
    ) -> None:
        super().__init__(
            title=title, description=description, icon=icon,
            commandBarOn=commandBarOn, id=id, *args, **kwargs,
        )

    def _wInitializeUI(self, view: Type[CanvasBase] = GLCanvas) -> None:
        super()._wInitializeUI()

        streamView: CanvasBase | QWidget = view(bg="#1a1a1a")
        streamView.setObjectName(f"{self.OBJECT_NAME}_STREAM")
        streamView.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        streamView.setMinimumSize(320, 240)
        self.addWidget(streamView, stretch=1)
        streamView.setMinimumSize(320, 240)

        self._streamView = streamView

        clsName: str = type(self).__name__
        verbose(
            f"[{clsName}] PlaybackBase id={self.Id!r} "
            f"class={clsName} stream={streamView.objectName()!r}"
        )
