# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List

# ==================================================================================
from adbutils import AdbDevice, adb
from PySide6.QtWidgets import QBoxLayout

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from jAGQt.types.interface.widgets.commandBar import iCommandBar, iCommandBarButton
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets.commandBar import CommandBar

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
from ..UI.widgets.streamer import imageStreamer


# ==================================================================================
class Shell(iShell):
    def _wInitializeShell(self: iMainWindowBase) -> None:
        try:            
            layout: QBoxLayout = self.Layout
            layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self.ContentSpacing = 0
            self.ContentMargins = 0

            image: imageStreamer = imageStreamer()

            commandBar: iCommandBar = CommandBar()
            cmdBtn: iCommandBarButton = commandBar.addButton("File")
            cmdBtn.clicked.connect(lambda: print("File"))
            commandBar.addStretch()

            layout.addWidget(image)
            layout.addWidget(commandBar)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeUI FAIL", ex)

    def _wInitializeSideBar(self: iMainWindowBase) -> None:
        pass

    # ==================================================================================    
    def initializeInstance(self: iMainWindowBase) -> None:
        try:
            devices: Dict[str, AdbDevice] = {d.serial: d for d in adb.device_list()}
            device: AdbDevice = devices.get("emulator-5560", None)
            if device is None: return
            emitter: SCRCPYEmitter = SCRCPYEmitter(device)
            emitter.subscribe("ON_FRAME", lambda frame: print(frame))
            emitter.start()

            self._emitter = emitter

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeInstance FAIL", ex)

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
