# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from adbutils import AdbDevice, adb


# ==================================================================================
def getADBDevice(
    device: Optional[Union[AdbDevice, str, None]], returnFirst: bool = False
) -> Optional[AdbDevice]:
    if isinstance(device, AdbDevice):
        return device

    _device: Optional[AdbDevice] = None
    if isinstance(device, str) and device != "":
        try:
            _device = adb.device(serial=device)
            return _device

        except Exception:
            pass

    if _device is None and returnFirst:
        devices = adb.device_list()
        _device = devices[0] if len(devices) > 0 else None
        return _device

    warning(f"Device {device} not found")
    return None
