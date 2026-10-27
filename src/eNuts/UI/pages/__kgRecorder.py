# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap

# ==================================================================================
from .__playbackBase import PlaybackBase


# ==================================================================================
class KGRecorder(PlaybackBase):
    """Key & Gesture Recorder page (view only).

    Inherits playback layout (Page chrome + GLImage). Emitter / controller
    wiring is deferred. Application controller remains
    eNuts.application.recorder.KGRecorder.
    """

    OBJECT_NAME = "W_KG_RECORDER"

    def __init__(
        self,
        title: str,
        description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        commandBarOn: bool = False,
        id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            title=title,
            description=description,
            icon=icon,
            commandBarOn=commandBarOn,
            id=id,
            *args,
            **kwargs,
        )

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()
        # Stream surface comes from PlaybackBase (_streamView).
        # Recorder-specific chrome (command bar, device strip) added later.
        verbose(f"[pages] KGRecorder page id={self.Id!r}")
