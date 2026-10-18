# ==================================================================================================
from asyncio import to_thread
from typing import Dict, List

# ==================================================================================================
from adbutils import AdbDevice, adb
from adbutils.errors import AdbError

# ==================================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.emitters import iSCRCPYEmitter


# ==================================================================================================
async def ADBDevices() -> Dict[str, AdbDevice]:
    deviceList: List[AdbDevice] = await to_thread(adb.device_list)
    devices: List[AdbDevice] = list(deviceList)
    return {d.serial: d for d in (devices or [])}


async def ADBShell(device: AdbDevice, cmd: str) -> str:
    try:
        return await to_thread(device.shell, cmd)

    except RuntimeError as ex:
        if ex.args[0] == "no running event loop":
            warning(f"Device {device.serial} not found")
            return None

        raise ex


async def SCRCPYDevices() -> Dict[str, iSCRCPYEmitter]:
    """Discover ADB devices and return **uninitialized** global emitters.

    Construct only — do not call ``initialize()`` / ``start()`` here. Ownership
    and lifecycle live in ``deviceManager`` (reuse on poll; stop on remove).
    """
    adbDevices: Dict[str, AdbDevice] = await ADBDevices()
    scrcpyDevices: Dict[str, iDevice] = {}
    for d in adbDevices.values():
        serial: str = d.serial
        try:
            model: str = await ADBShell(d, "getprop ro.product.model")
            manufacturer: str = await ADBShell(d, "getprop ro.product.manufacturer")
        except AdbError:
            continue

        display = (model or "").strip() or (manufacturer or "").strip() or serial
        # Global emitter handle for this serial (not started yet).
        emitter: iSCRCPYEmitter = SCRCPYEmitter(serial, display)
        scrcpyDevices[serial] = emitter

    return scrcpyDevices
