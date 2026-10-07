# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtWidgets import QBoxLayout

from jAGQt.types.interface.widgets.commandBar import iCommandBar

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets.commandBar import CommandBar

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell


# ==================================================================================
class Shell(iShell):
    def _wIntializeUI(self: iMainWindowBase) -> None:
        try:
            layout: QBoxLayout = self.Layout
            layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self.ContentSpacing = 0
            self.ContentMargins = 0

            commandBar: iCommandBar = CommandBar()
            commandBar.addButton("File")
            layout.addStretch()
            layout.addWidget(commandBar)


        except Exception as ex:
            error("[shell] intializeUI FAIL", ex)

    def _wInitializeSideBar(self: iMainWindowBase) -> None:
        # self._sideBar: iSideBar = SideBar(self)
        pass

    # ==================================================================================    
    def initializeInstance(self: iMainWindowBase) -> None:
        pass

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
