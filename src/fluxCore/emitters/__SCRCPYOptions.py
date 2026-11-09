# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
JAR_NAME = "scrcpy-server.jar"
SERVER_PATH = os.path.join(os.getcwd(), ".bin", JAR_NAME)
ANDROID_PATH = "/data/local/tmp/"
MAX_SIZE = 1080
MAX_FPS = 60
BITRATE = 10000000
# ==================================================================================


# ==================================================================================
class SCRCPYOptions(Serializable):
    def __init__(
        self,
        serverPath: str = SERVER_PATH,
        androidPath: str = ANDROID_PATH,
        maxSize: int = MAX_SIZE,
        maxFps: int = MAX_FPS,
        bitrate: int = BITRATE,
    ) -> None:
        super().__init__()
        self._serverPath: str = serverPath
        self._androidPath: str = androidPath
        self._maxSize: int = maxSize
        self._maxFps: int = maxFps
        self._bitrate: int = bitrate
        self._jarName: str = JAR_NAME

        self.Properties.extend(
            ["serverPath", "androidPath", "maxSize", "maxFps", "bitrate"]
        )

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
