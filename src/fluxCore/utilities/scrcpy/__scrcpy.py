# ==================================================================================
from os import getcwd, path
from socket import socket
from time import sleep

# ==================================================================================
from adbutils import AdbConnection, AdbDevice, AdbError, Network

# ==================================================================================
from ...configurations.scrcpy.__scrcpyConfig import SCRCPYServerConfig

# ==================================================================================
G_SCRCPY_JAR_NAME = "scrcpy-server.jar"
G_SCRCPY_SERVER_PATH = path.join(getcwd(), ".bin", G_SCRCPY_JAR_NAME)
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

#================================,
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
def isSCRCPYServerDeployed( device: AdbDevice, path: str = G_SCRCPY_ANDROID_PATH, JARName: str = G_SCRCPY_JAR_NAME):
    try:
        for info in device.sync.list(path):
            if info.path == JARName:
                return True

        return False

    except AdbError:
        return False


# ==================================================================================
def pushSCRCPYServer(
    device: AdbDevice,
    androidPath: str = G_SCRCPY_ANDROID_PATH, serverPath: str = G_SCRCPY_SERVER_PATH,
    JARName: str = G_SCRCPY_JAR_NAME, timeout: int = 3000,
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
    device: AdbDevice,
    cfg: SCRCPYServerConfig,
    serverPath: str = G_SCRCPY_SERVER_PATH,
    timeout: int = 3000,
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


