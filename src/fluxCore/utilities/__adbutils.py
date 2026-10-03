# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from adbutils import AdbDevice, adb


# ==================================================================================
def getADBDevice(device: Optional[Union[AdbDevice, str, None]], getFirst: bool = False) -> Optional[AdbDevice]:
    if isinstance(device, AdbDevice): return device

    lDevice: AdbDevice = None
    if isinstance(device, str) and device != "":
        try:
            lDevice = AdbDevice(serial=device)
            return lDevice

        except Exception as e:
            pass
    
    if lDevice is None and getFirst:
        lDevices = adb.device_list()
        lDevice: AdbDevice = lDevices[0] if len(lDevices) > 0 else None

    warning(f"Device {device} not found")
    return None
