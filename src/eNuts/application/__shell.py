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

            self._imageStreamer: imageStreamer = imageStreamer()

            commandBar: iCommandBar = CommandBar()
            cmdBtn: iCommandBarButton = commandBar.addButton("File")
            commandBar.addStretch()

            layout.addWidget(self._imageStreamer)
            layout.addWidget(commandBar)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeUI FAIL", ex)

    def _wInitializeSideBar(self: iMainWindowBase) -> None:
        pass

    # ==================================================================================
    async def initializeInstance(self: iMainWindowBase) -> None:
        try:
            emitter: SCRCPYEmitter = SCRCPYEmitter("emulator-5560")
            await emitter.initialize()

            self._imageStreamer.Decoder = emitter.CodecContext
            self._imageStreamer.ControlSocket = emitter.ControlSocket
            self._imageStreamer.DeviceWidth = emitter.width
            self._imageStreamer.DeviceHeight = emitter.height

            emitter.subscribe("ON_FRAME", self._imageStreamer.OnFrame)
            emitter.start()

            self._emitter = emitter

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeInstance FAIL", ex)

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
