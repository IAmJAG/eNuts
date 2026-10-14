# ==================================================================================
# src/eNuts/UI/widgets/pages/recorder/__recorderPage.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING

from jAGFx.workflow import workflow

# ==================================================================================
from jAGQt.widgets import Page

# ==================================================================================
if TYPE_CHECKING:
    from .....types.interface.application import iShell


# ==================================================================================
@workflow
class KAndGRecorderPage(Page):
    def __init__(self, shell: iShell | None = None, parent=None) -> None:
        super().__init__(
            title="K&G Recorder",
            description="Key & Gesture Recorder",
            parent=parent,
        )
        self.setObjectName("KAndGRecorderPage")
        self._shell: iShell | None = shell
