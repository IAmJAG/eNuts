## Overview & Design Context
Base serializable device representation used across fluxCore and eNuts clients. Holds identity, name, and screen dimensions. Concrete subclasses implement `updateInfo` for platform-specific queries (e.g. ADB).

* **Design Decision / Deviation Notes:** Properties trigger `updateInfo` lazily when name/width/height are missing. Serializable via jAGFx.serializer. Implements `iDevice`.

---

## Classes

### `Device`
- **Purpose:** Core device identity and geometry holder. Serializable. Base for SCRCPYDevice and other device types.
- **Methods:**
  - `__init__(ident=None, name=None, width=None, height=None)` — initializes id (UUID or provided), name, width, height; extends Properties for serialization.
  - `updateInfo()` — stub; warns that it is not implemented (override in subclasses).
- **Properties:**
  - `id` → str/UUID
  - `name` → Optional[str] (lazy updateInfo)
  - `width` → int (lazy)
  - `height` → int (lazy)

## Sample Usage

```python
from fluxCore.device import Device

dev = Device(ident="emulator-5554", name="Test", width=1080, height=1920)
print(dev.id, dev.name)
```
