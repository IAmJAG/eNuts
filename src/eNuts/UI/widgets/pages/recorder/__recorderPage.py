# ==================================================================================
# src/eNuts/UI/widgets/pages/recorder/__recorderPage.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.widgets import CommandBar, Page


# ==================================================================================
class KAndGRecorderPage(Page):
    """Key & Gesture Recorder page (Phase 1 stub).

    Full Stream / Configuration tabs, RecorderImage, and recording
    lifecycle are implemented in subsequent phases.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(
            title="K&G Recorder",
            description="Key & Gesture Recorder — live scrcpy stream with action capture",
            parent=parent,
        )
        lBar = CommandBar(parent=self)
        self.CommandBar = lBar
