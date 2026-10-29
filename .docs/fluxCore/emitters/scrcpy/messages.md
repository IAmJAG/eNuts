## Overview & Design Context

IPC message types for the SCRCPY domain bridge. Implemented under `src/fluxCore/emitters/scrcpy/` (not under `jAGFx.IPC`).

Handlers on `Bridge` key off **message type** (`type(message)`).

---

## Classes

### `ScrcpyInitParams` (`__payloads.py`)

- **Purpose:** Body for `ScrcpyInitializeMessage`.
- **Properties:** `serial`, `gpuId`, `gpuReady`

### `ScrcpyInitializeMessage`

- **Direction:** main → client  
- **Payload:** `ScrcpyInitParams`  
- **Correlation:** yes; complete with terminal metadata or terminal error

### `ScrcpyStartMessage` / `ScrcpyStopMessage`

- **Direction:** main → client  
- **Payload:** none  
- **Correlation:** fire-and-forget

### `ScrcpyMetadataMessage`

- **Direction:** client → main  
- **Payload:** base `SCRCPY` (from `toScrcpy`)  
- **Terminal:** set when ending a successful initialize conversation

### `ScrcpyErrorMessage`

- **Direction:** client → main  
- **Payload:** `SCRCPYError`  
- **Terminal:** set when ending a failed initialize conversation

---

## Sample Usage

```python
from fluxCore.emitters.scrcpy import (
    ScrcpyInitParams,
    ScrcpyInitializeMessage,
    ScrcpyMetadataMessage,
    ScrcpyErrorMessage,
    SCRCPYError,
)

params = ScrcpyInitParams(serial="DEVICE", gpuId=0, gpuReady=True)
msg = ScrcpyInitializeMessage(payload=params)

# success: ScrcpyMetadataMessage(..., correlationId=msg.correlationId, isTerminal=True)
# failure: ScrcpyErrorMessage(payload=SCRCPYError(...), correlationId=..., isTerminal=True)
```
