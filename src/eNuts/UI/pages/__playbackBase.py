# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QSizePolicy

# ==================================================================================
from jAGQt.widgets import GLImage
from jAGQt.widgets.page import Page


# ==================================================================================
class PlaybackBase(Page):
    OBJECT_NAME = "W_PLAYBACK"

    def __init__(
        self, title: str, description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        commandBarOn: bool = False, id: Optional[str] = None,
        *args, **kwargs,
    ) -> None:
        super().__init__(
            title=title, description=description, icon=icon,
            commandBarOn=commandBarOn, id=id, *args, **kwargs,
        )

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()

        streamView = GLImage(bg="#1a1a1a")
        streamView.setObjectName(f"{self.OBJECT_NAME}_STREAM")
        streamView.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        streamView.setMinimumSize(320, 240)
        self.addWidget(streamView, stretch=1)

        self._streamView = streamView

        verbose(
            f"[pages] PlaybackBase id={self.Id!r} "
            f"class={type(self).__name__} stream={streamView.objectName()!r}"
        )
