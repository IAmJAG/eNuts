# ==================================================================================
from os import path
from threading import Lock
from typing import Optional, Set


# ==================================================================================
class SCRCPYServerConfig:
    CL_DEFAULT_VERSION = "2.4"
    CL_DEFAULT_MAX_SIZE = 1920
    CL_DEFAULT_MAX_FPS = 60
    CL_DEFAULT_BITRATE = 8_000_000
    CL_DEFAULT_LOG_LEVEL = "info"
    CL_DEFAULT_VIDEO_ENCODER = ""  # empty = let server choose HW encoder
    CL_DEFAULT_VIDEO_CODEC = "h264"
    CL_DEFAULT_TUNNEL_FORWARD = True
    CL_DEFAULT_SEND_FRAME_META = True
    CL_DEFAULT_CONTROL = True
    CL_DEFAULT_AUDIO = False
    CL_DEFAULT_SHOW_TOUCHES = False
    CL_DEFAULT_STAY_AWAKE = False
    CL_DEFAULT_POWER_OFF_ON_CLOSE = False
    CL_DEFAULT_CLIPBOARD_AUTOSYNC = False
    CL_DEFAULT_DISPLAY_ID = 0
    CL_DEFAULT_CLEANUP = False  # leave JAR on device by default

    # Sequential SCID registry (process-wide)
    _scid_lock: Lock = Lock()
    _used_scids: Set[int] = set()
    _next_scid: int = 1

    def __init__(
        self,
        androidPath: str,
        jarName: str,
        version: str = CL_DEFAULT_VERSION,
        maxSize: int = CL_DEFAULT_MAX_SIZE,
        maxFps: int = CL_DEFAULT_MAX_FPS,
        bitrate: int = CL_DEFAULT_BITRATE,
        logLevel: str = CL_DEFAULT_LOG_LEVEL,
        videoEncoder: str = CL_DEFAULT_VIDEO_ENCODER,
        videoCodec: str = CL_DEFAULT_VIDEO_CODEC,
        tunnelForward: bool = CL_DEFAULT_TUNNEL_FORWARD,
        sendFrameMeta: bool = CL_DEFAULT_SEND_FRAME_META,
        control: bool = CL_DEFAULT_CONTROL,
        audio: bool = CL_DEFAULT_AUDIO,
        showTouches: bool = CL_DEFAULT_SHOW_TOUCHES,
        stayAwake: bool = CL_DEFAULT_STAY_AWAKE,
        powerOffOnClose: bool = CL_DEFAULT_POWER_OFF_ON_CLOSE,
        clipboardAutosync: bool = CL_DEFAULT_CLIPBOARD_AUTOSYNC,
        displayId: int = CL_DEFAULT_DISPLAY_ID,
        cleanup: bool = CL_DEFAULT_CLEANUP,
        scid: Optional[int] = None,
    ) -> None:
        self._androidPath = androidPath
        self._jarName = jarName
        self._version = version
        self._maxSize = maxSize
        self._maxFps = maxFps
        self._bitrate = bitrate
        self._logLevel = logLevel
        self._videoEncoder = videoEncoder
        self._videoCodec = videoCodec
        self._tunnelForward = tunnelForward
        self._sendFrameMeta = sendFrameMeta
        self._control = control
        self._audio = audio
        self._showTouches = showTouches
        self._stayAwake = stayAwake
        self._powerOffOnClose = powerOffOnClose
        self._clipboardAutosync = clipboardAutosync
        self._displayId = displayId
        self._cleanup = cleanup

        if scid is None:
            self._scid = self._allocate_scid()

        else:
            self._register_scid(scid)
            self._scid = scid

    # -------------------------------------------------------------------------
    # SCID registry
    # -------------------------------------------------------------------------
    @classmethod
    def _allocate_scid(cls) -> int:
        with cls._scid_lock:
            while cls._next_scid in cls._used_scids:
                cls._next_scid = (cls._next_scid + 1) & 0x7FFFFFFF
                if cls._next_scid == 0:
                    cls._next_scid = 1
            scid = cls._next_scid
            cls._used_scids.add(scid)
            cls._next_scid = (cls._next_scid + 1) & 0x7FFFFFFF
            if cls._next_scid == 0:
                cls._next_scid = 1
            return scid

    @classmethod
    def _register_scid(cls, scid: int) -> None:
        if scid < 0 or scid > 0x7FFFFFFF: raise ValueError(f"scid must be 0..0x7FFFFFFF, got {scid}")

        with cls._scid_lock:
            if scid in cls._used_scids:
                raise ValueError(f"scid {scid:#x} already in use")
            
            cls._used_scids.add(scid)

    @classmethod
    def release_scid(cls, scid: int) -> None:
        """Call when the corresponding server process ends."""
        with cls._scid_lock:
            cls._used_scids.discard(scid)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    @property
    def AndroidPath(self) -> str:
        return self._androidPath

    @AndroidPath.setter
    def AndroidPath(self, androidPath: str) -> None:
        self._androidPath = androidPath

    @property
    def JarName(self) -> str:
        return self._jarName

    @JarName.setter
    def JarName(self, jarName: str) -> None:
        self._jarName = jarName

    @property
    def Version(self) -> str:
        return self._version

    @Version.setter
    def Version(self, version: str) -> None:
        self._version = version

    @property
    def Scid(self) -> int:
        return self._scid

    @property
    def MaxSize(self) -> int:
        return self._maxSize

    @MaxSize.setter
    def MaxSize(self, maxSize: int) -> None:
        self._maxSize = maxSize

    @property
    def MaxFps(self) -> int:
        return self._maxFps

    @MaxFps.setter
    def MaxFps(self, maxFps: int) -> None:
        self._maxFps = maxFps

    @property
    def Bitrate(self) -> int:
        return self._bitrate

    @Bitrate.setter
    def Bitrate(self, bitrate: int) -> None:
        self._bitrate = bitrate

    @property
    def LogLevel(self) -> str:
        return self._logLevel

    @LogLevel.setter
    def LogLevel(self, logLevel: str) -> None:
        self._logLevel = logLevel

    @property
    def VideoEncoder(self) -> str:
        return self._videoEncoder

    @VideoEncoder.setter
    def VideoEncoder(self, videoEncoder: str) -> None:
        self._videoEncoder = videoEncoder

    @property
    def VideoCodec(self) -> str:
        return self._videoCodec

    @VideoCodec.setter
    def VideoCodec(self, videoCodec: str) -> None:
        self._videoCodec = videoCodec

    @property
    def TunnelForward(self) -> bool:
        return self._tunnelForward

    @TunnelForward.setter
    def TunnelForward(self, tunnelForward: bool) -> None:
        self._tunnelForward = tunnelForward

    @property
    def SendFrameMeta(self) -> bool:
        return self._sendFrameMeta

    @SendFrameMeta.setter
    def SendFrameMeta(self, sendFrameMeta: bool) -> None:
        self._sendFrameMeta = sendFrameMeta

    @property
    def Control(self) -> bool:
        return self._control

    @Control.setter
    def Control(self, control: bool) -> None:
        self._control = control

    @property
    def Audio(self) -> bool:
        return self._audio

    @Audio.setter
    def Audio(self, audio: bool) -> None:
        self._audio = audio

    @property
    def ShowTouches(self) -> bool:
        return self._showTouches

    @ShowTouches.setter
    def ShowTouches(self, showTouches: bool) -> None:
        self._showTouches = showTouches

    @property
    def StayAwake(self) -> bool:
        return self._stayAwake

    @StayAwake.setter
    def StayAwake(self, stayAwake: bool) -> None:
        self._stayAwake = stayAwake

    @property
    def PowerOffOnClose(self) -> bool:
        return self._powerOffOnClose

    @PowerOffOnClose.setter
    def PowerOffOnClose(self, powerOffOnClose: bool) -> None:
        self._powerOffOnClose = powerOffOnClose

    @property
    def ClipboardAutosync(self) -> bool:
        return self._clipboardAutosync

    @ClipboardAutosync.setter
    def ClipboardAutosync(self, clipboardAutosync: bool) -> None:
        self._clipboardAutosync = clipboardAutosync

    @property
    def DisplayId(self) -> int:
        return self._displayId

    @DisplayId.setter
    def DisplayId(self, displayId: int) -> None:
        self._displayId = displayId

    @property
    def Cleanup(self) -> bool:
        return self._cleanup

    @Cleanup.setter
    def Cleanup(self, cleanup: bool) -> None:
        self._cleanup = cleanup

    # -------------------------------------------------------------------------
    def buildCommands(self) -> list[str]:
        androidPath = path.join(self._androidPath, self._jarName).replace("\\", "/")
        cmds = [
            f"CLASSPATH={androidPath}",
            "app_process",
            "/",
            "com.genymobile.scrcpy.Server",
            self._version,
            f"scid={self._scid:08x}",
            f"log_level={self._logLevel}",
            f"max_size={self._maxSize}",
            f"max_fps={self._maxFps}",
            f"video_bit_rate={self._bitrate}",
            f"video_codec={self._videoCodec}",
            f"tunnel_forward={str(self._tunnelForward).lower()}",
            f"send_frame_meta={str(self._sendFrameMeta).lower()}",
            f"control={str(self._control).lower()}",
            f"audio={str(self._audio).lower()}",
            f"show_touches={str(self._showTouches).lower()}",
            f"stay_awake={str(self._stayAwake).lower()}",
            f"power_off_on_close={str(self._powerOffOnClose).lower()}",
            f"clipboard_autosync={str(self._clipboardAutosync).lower()}",
            f"display_id={self._displayId}",
            f"cleanup={str(self._cleanup).lower()}",
        ]
        if self._videoEncoder:
            cmds.append(f"video_encoder={self._videoEncoder}")
        return cmds

    def __repr__(self) -> str:
        return (
            f"ScrcpyServerConfig("
            f"version={self._version!r}, "
            f"scid={self._scid:#010x}, "
            f"androidPath={self._androidPath!r}, "
            f"jarName={self._jarName!r}, "
            f"cleanup={self._cleanup}, "
            f"...)"
        )
