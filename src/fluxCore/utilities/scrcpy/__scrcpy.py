# ==================================================================================
from os import getcwd, path
from socket import AF_INET, SOCK_STREAM, socket
from time import sleep
from typing import Optional, Union

# ==================================================================================
from adbutils import AdbConnection, AdbDevice, AdbError, Network
from av import CodecContext, VideoCodecContext

# ==================================================================================
from .__scrcpyConfig import SCRCPYServerConfig

# ==================================================================================
JAR_NAME = "scrcpy-server.jar"
SERVER_PATH = path.join(getcwd(), ".bin", JAR_NAME)
ANDROID_PATH = "/data/local/tmp/"
MAX_SIZE = 0
MAX_FPS = 0
BITRATE = 4000000
# ==================================================================================

try:
    from av.codec.hwaccel import HWAccel, hwdevices_available

    C_HAS_HWACCEL = True

except ImportError:
    debug(
        "WARNING: decodeToGpu=True requires a PyAV build with av.codec.hwaccel.HWAccel. "
    )
    HWAccel = None
    hwdevices_available = None
    C_HAS_HWACCEL = False

# ==================================================================================
def isSCRCPYServerDeployed(
    device: AdbDevice, path: str = ANDROID_PATH, JARName: str = JAR_NAME
):
    try:
        for info in device.sync.list(path):
            if info.path == JARName:
                return True

        return False

    except AdbError:
        return False


# ==================================================================================
def pushSCRCPYServer(
    device: AdbDevice, androidPath: str = ANDROID_PATH,
    serverPath: str = SERVER_PATH, JARName: str = JAR_NAME,
    timeout: int = 3000,
):
    # retry every 100ms
    for _ in range(timeout // 100):
        try:
            if isSCRCPYServerDeployed(device, androidPath, JARName):
                return True

            device.sync.push(serverPath, androidPath)
            return True

        except AdbError as ex:
            sleep(0.01)

        except Exception as ex:
            debug(f"Error pushing scrcpy server {ex}")
            raise ex

    else:
        raise ConnectionError(
            f"Failed to push scrcpy server file after {timeout / 1000} seconds"
        )


def deployServer(
    device: AdbDevice, cfg: SCRCPYServerConfig,
    serverPath: str = SERVER_PATH, timeout: int = 3000,
) -> AdbConnection:
    try:
        androidPath: str = cfg.AndroidPath
        jarName: str = cfg.JarName

        if not pushSCRCPYServer(device, androidPath, serverPath, jarName, timeout):
            raise Exception("Could not deploy scrcpy server")

        cmds: list[str] = cfg.buildCommands()
        lCmd: str = " ".join(cmds)
        strmServer: AdbConnection = device.shell(lCmd, stream=True)
        if strmServer is None:
            raise Exception("Could not start scrcpy server")

        return strmServer

    except Exception as ex:
        raise ex


# ==================================================================================
def getSCRCPYADBSocket(device: AdbDevice, scid: str, timeout: int = 3000) -> socket:
    sSocket: socket = None
    name = "scrcpy" if scid < 0 else f"scrcpy_{scid:08x}"
    # retry every 100ms
    for _ in range(timeout // 100):
        try:
            sSocket: socket = device.create_connection(Network.LOCAL_ABSTRACT, name)
            break

        except AdbError:
            sleep(0.01)

    else:
        raise ConnectionError("Failed to connect scrcpy-server after 3 seconds")

    return sSocket


# ==================================================================================
def createCodecContext(
    codecId: str, GPUID: int = 0, GPUReady: bool = True
) -> VideoCodecContext:
    lCodec = (codecId or "h264").strip().lower() or "h264"

    if not GPUReady:
        return CodecContext.create(lCodec, "r")

    if not C_HAS_HWACCEL:
        raise RuntimeError(
            "decodeToGpu=True requires a PyAV build with av.codec.hwaccel.HWAccel. "
            "Upgrade PyAV or set decodeToGpu=False."
        )

    lDevices = list(hwdevices_available() or [])
    if "cuda" not in lDevices:
        raise RuntimeError(
            f"decodeToGpu=True needs FFmpeg/PyAV CUDA hwaccel; available={lDevices}. "
            "Rebuild FFmpeg with NVDEC/cuvid support or set decodeToGpu=False."
        )

    lHwaccel = HWAccel(
        device_type="cuda",
        device=str(GPUID),
        allow_software_fallback=False,
        is_hw_owned=True,
    )
    lCtx = CodecContext.create(lCodec, "r", hwaccel=lHwaccel)

    try:
        lCtx.options = {"flags": "low_delay"}

    except Exception:
        pass

    return lCtx
