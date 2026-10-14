# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from adbutils import AdbDevice, adb


# ==================================================================================
def getADBDevice(
    device: Optional[Union[AdbDevice, str, None]], getFirst: bool = False
) -> Optional[AdbDevice]:
    if isinstance(device, AdbDevice):
        return device

    lDevice: AdbDevice | None = None
    if isinstance(device, str) and device != "":
        try:
            lDevice = adb.device(serial=device)
            return lDevice

        except Exception:
            pass

    if lDevice is None and getFirst:
        lDevices = adb.device_list()
        lDevice = lDevices[0] if len(lDevices) > 0 else None
        if lDevice is not None:
            return lDevice

    warning(f"Device {device} not found")
    return None
