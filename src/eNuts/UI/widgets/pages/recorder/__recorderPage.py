# ==================================================================================
# src/eNuts/UI/widgets/pages/recorder/__recorderPage.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING

# ==================================================================================
from jAGQt.widgets import Page

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.application import iShell


# ==================================================================================
class KAndGRecorderPage(Page):
    """Key & Gesture Recorder — Phase 1 stub.

    Registered under Data Factory(DF). Full Stream / Configuration UI and
    recording lifecycle belong to later phases.
    """

    def __init__(self, shell: iShell | None = None, parent=None) -> None:
        super().__init__(
            title="K&G Recorder",
            description="Key & Gesture Recorder",
            parent=parent,
        )
        self.setObjectName("KAndGRecorderPage")
        self._shell: iShell | None = shell
