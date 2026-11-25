## Overview & Design Context
SCRCPY-specific device that queries ADB for model, manufacturer, and window size. Subclass of Device.

* **Design Decision / Deviation Notes:** Uses adbutils to shell getprop and window_size. Name formatted as "manufacturer:model".

---

## Classes

### `SCRCPYDevice`
- **Purpose:** Concrete Device for ADB/SCRCPY serials. Populates geometry and friendly name from device properties.
- **Methods:**
  - `__init__(ident=None, name=None, width=None, height=None)` — delegates to Device.
  - `updateInfo()` — queries adb.device(serial).window_size() and getprop for manufacturer/model; sets _name, _width, _height.

## Sample Usage

```python
from fluxCore.device import SCRCPYDevice

dev = SCRCPYDevice(ident="R58N123456")
dev.updateInfo()
print(dev.name, dev.width, dev.height)
```
