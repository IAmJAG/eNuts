# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap

# ==================================================================================
from .__playbackBase import PlaybackBase


# ==================================================================================
class Annotator(PlaybackBase):
    """Video / image annotator page (view only).

    Inherits playback layout (Page chrome + GLImage). Annotation tools and
    stream attach are deferred.
    """

    OBJECT_NAME = "W_ANNOTATOR"

    def __init__(
        self, title: str, description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None, commandBarOn: bool = False,
        id: Optional[str] = None, *args, **kwargs,
    ) -> None:
        super().__init__(title=title, description=description, icon=icon,
            commandBarOn=commandBarOn, id=id, *args, **kwargs,
        )

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()
        verbose(f"[pages] Annotator page id={self.Id!r}")
