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
    def __init__(
        self, title: str, description: str,
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        commandBarOn: bool = False, id: Optional[str] = None, *args, **kwargs
    ) -> None:
        super().__init__(
            title=title, description=description, icon=icon,
            commandBarOn=commandBarOn, id=id, *args, **kwargs,
        )

    def className(self) -> str:
        return type(self).__name__

    def _wInitializeUI(self, view: Type[CanvasBase] = GLCanvas) -> None:
        super()._wInitializeUI()

        streamView: QWidget = view(bg="##1a1a1a")
        streamView.setObjectName(f"{self.OBJECT_NAME}_STREAM")
        streamView.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )        
        self.addWidget(streamView, stretch=1)
        streamView.setMinimumSize(320, 240)

        self._streamView = streamView
        verbose(
            f"[{self.className()}] PlaybackBase id={self.Id!r} "
            f"class={self.className()} stream={streamView.objectName()!r}"
        )
