# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from typing import Optional

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
G_SCRCPY_JAR_NAME = "scrcpy-server.jar"
G_SCRCPY_SERVER_PATH = os.path.join(os.getcwd(), ".bin", G_SCRCPY_JAR_NAME)
G_SCRCPY_ANDROID_PATH = "/data/local/tmp/"
G_SCRCPY_MAX_SIZE = 0
G_SCRCPY_MAX_FPS = 0
G_SCRCPY_BITRATEMAP: dict[int, int] = {
    540: 2000000,
    720: 4000000,
    900: 6000000,
    1080: 8000000,
    1280: 10000000,
    1440: 12000000,
    1600: 14000000,
    1920: 12000000,
    2560: 16000000,
    3200: 24000000,
}


# ==================================================================================
class SCRCPYConfig(Serializable):
    _scidSet: set[int] = set[int]()
    def __init__(
        self, serverPath: str = G_SCRCPY_SERVER_PATH, androidPath: str = G_SCRCPY_ANDROID_PATH, 
        maxSize: int = G_SCRCPY_MAX_SIZE, maxFps: int = G_SCRCPY_MAX_FPS
    ) -> None:
        super().__init__()
        self._serverPath: str = serverPath
        self._androidPath: str = androidPath
        self._maxSize: int = maxSize
        self._maxFps: int = maxFps        
        self._jarName: str = G_SCRCPY_JAR_NAME

        self._bitrate: int = G_SCRCPY_BITRATEMAP[maxSize] if maxSize in G_SCRCPY_BITRATEMAP.keys() else 0
        
        self.Properties.extend(
            ["serverPath", "androidPath", "maxSize", "maxFps", "bitrate"]
        )

        self._version: str = "2.4"
        self._logLevel: str = "info"
        self._videoCodec: str = "h264"
        self._tunnelForward: bool = True
        self._sendFrameMeta: bool = True
        self._control: bool = True
        self._audio: bool = False
        self._showTouches: bool = False
        self._stayAwake: bool = False
        self._powerOffOnClose: bool = False
        self._clipboardAutosync: bool = False
        self._displayId: int = 0
        self._cleanup: bool = False

        self._scid: Optional[int] = None

    # -------------------------------------------------------------------------
    def buildCommands(self) -> list[str]:
        androidPath = os.path.join(self._androidPath, self._jarName).replace("\\", "/")

        cmds = [
            f"CLASSPATH={androidPath}",
            "app_process",
            "/",
            "com.genymobile.scrcpy.Server",
            self._version,
            f"log_level={self._logLevel}",
            f"scid={self._scid}",
        ]

        if self._maxSize > 0: cmds.append(f"max_size={self._maxSize}")
        if self._maxFps > 0: cmds.append(f"max_fps={self._maxFps}")
        if self._bitrate > 0: cmds.append(f"video_bit_rate={self._bitrate}")
        if self._videoCodec: cmds.append(f"video_codec={self._videoCodec}")
        if self._tunnelForward: cmds.append(f"tunnel_forward={str(self._tunnelForward).lower()}")
        if self._sendFrameMeta: cmds.append(f"send_frame_meta={str(self._sendFrameMeta).lower()}")
        if self._control: cmds.append(f"control={str(self._control).lower()}")
        if self._audio: cmds.append(f"audio={str(self._audio).lower()}")
        if self._showTouches: cmds.append(f"show_touches={str(self._showTouches).lower()}")
        if self._stayAwake: cmds.append(f"stay_awake={str(self._stayAwake).lower()}")
        if self._powerOffOnClose: cmds.append(f"power_off_on_close={str(self._powerOffOnClose).lower()}")
        if self._clipboardAutosync: cmds.append(f"clipboard_autosync={str(self._clipboardAutosync).lower()}")        
        if self._displayId > 0: cmds.append(f"display_id={self._displayId}")
        if self._cleanup: cmds.append(f"cleanup={str(self._cleanup).lower()}")        
        
        return cmds

    @property
    def serverPath(self) -> str:
        return self._serverPath

    @property
    def androidPath(self) -> str:
        return self._androidPath

    @property
    def maxSize(self) -> int:
        return self._maxSize

    @property
    def maxFps(self) -> int:
        return self._maxFps

    @property
    def bitrate(self) -> int:
        return self._bitrate

    @serverPath.setter
    def serverPath(self, value: str) -> None:
        self._serverPath = value

    @androidPath.setter
    def androidPath(self, value: str) -> None:
        self._androidPath = value

    @maxSize.setter
    def maxSize(self, value: int) -> None:
        self._maxSize = value

    @maxFps.setter
    def maxFps(self, value: int) -> None:
        self._maxFps = value

    @bitrate.setter
    def bitrate(self, value: int) -> None:
        self._bitrate = value

    @property
    def jarName(self) -> str:
        return self._jarName

    @jarName.setter
    def jarName(self, value: str) -> None:
        self._jarName = value

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    @property
    def logLevel(self) -> str:
        return self._logLevel

    @logLevel.setter
    def logLevel(self, value: str) -> None:
        self._logLevel = value

    @property
    def videoCodec(self) -> str:
        return self._videoCodec

    @videoCodec.setter
    def videoCodec(self, value: str) -> None:
        self._videoCodec = value

    @property
    def tunnelForward(self) -> bool:
        return self._tunnelForward

    @tunnelForward.setter
    def tunnelForward(self, value: bool) -> None:
        self._tunnelForward = value

    @property
    def sendFrameMeta(self) -> bool:
        return self._sendFrameMeta

    @sendFrameMeta.setter
    def sendFrameMeta(self, value: bool) -> None:
        self._sendFrameMeta = value

    @property
    def control(self) -> bool:
        return self._control

    @control.setter
    def control(self, value: bool) -> None:
        self._control = value

    @property
    def audio(self) -> bool:
        return self._audio

    @audio.setter
    def audio(self, value: bool) -> None:
        self._audio = value

    @property
    def showTouches(self) -> bool:
        return self._showTouches

    @showTouches.setter
    def showTouches(self, value: bool) -> None:
        self._showTouches = value

    @property
    def stayAwake(self) -> bool:
        return self._stayAwake

    @stayAwake.setter
    def stayAwake(self, value: bool) -> None:
        self._stayAwake = value
    

    @property
    def powerOffOnClose(self) -> bool:
        return self._powerOffOnClose

    @powerOffOnClose.setter
    def powerOffOnClose(self, value: bool) -> None:
        self._powerOffOnClose = value


    @property
    def clipboardAutosync(self) -> bool:
        return self._clipboardAutosync

    @clipboardAutosync.setter
    def clipboardAutosync(self, value: bool) -> None:
        self._clipboardAutosync = value


    @property
    def displayId(self) -> int:
        return self._displayId

    @displayId.setter
    def displayId(self, value: int) -> None:
        self._displayId = value


    @property
    def cleanup(self) -> bool:
        return self._cleanup

    @cleanup.setter
    def cleanup(self, value: bool) -> None:
        self._cleanup = value


    @property
    def scid(self) -> set[int]:        
        if not self._scid:
            self._scid = 1
            while self._scid in self._scidSet:
                self._scid += 1
            self._scidSet.add(self._scid)

        return self._scid
    