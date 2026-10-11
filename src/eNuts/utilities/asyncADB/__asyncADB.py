# ==================================================================================================
from typing import Dict, List

# ==================================================================================================
from adbutils import AdbDevice, adb

# ==================================================================================================
from fluxCore.devices import SCRCPY
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.devices import iSCRCPY


# ==================================================================================================
async def ADBDevices() -> Dict[str, AdbDevice]:
    devices: List[AdbDevice] = list(adb.device_list())
    return {d.serial: d for d in (devices or [])}

async def ADBShell(device: AdbDevice, cmd: str) -> str:
    return device.shell(cmd)

async def SCRCPYDevices() -> Dict[str, iSCRCPY]:
    adbDevices: Dict[str, AdbDevice] = await ADBDevices()
    scrcpyDevices: Dict[str, iDevice] = {}
    for d in adbDevices.values():
        serial: str = d.serial
        model: str = await ADBShell(d, "getprop ro.product.model")
        manufacturer: str = await ADBShell(d, "getprop ro.product.manufacturer")
        scrcpy: iSCRCPY = SCRCPY(serial, model, manufacturer)
        scrcpyDevices[serial] = scrcpy

    return scrcpyDevices
