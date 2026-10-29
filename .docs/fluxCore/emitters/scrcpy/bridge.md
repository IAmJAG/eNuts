## Overview & Design Context

`ScrcpyRealBridge` (client) owns the emitter; `ScrcpyProxyBridge` (main) sends commands and receives metadata/errors. Both subclass `jAGFx.IPC.Bridge`.

Register with `asDefault=True` so application messages do not require `ownerId` routing.

---

## Classes

### `ScrcpyRealBridge`

- Handles `ScrcpyInitializeMessage` / `Start` / `Stop`.
- Success → terminal `ScrcpyMetadataMessage`; failure → terminal `ScrcpyErrorMessage`.
- Optional duck-typed emitter for tests (no ADB).

### `ScrcpyProxyBridge`

- `requestInitialize` / `requestStart` / `requestStop`.
- `lastMetadata` / `lastError` / asyncio events for waiters.

---

## Sample

```python
from fluxCore.emitters.scrcpy import ScrcpyRealBridge, ScrcpyProxyBridge, ScrcpyInitParams

real = ScrcpyRealBridge(emitter=stub_or_scrcpy_emitter)
proxy = ScrcpyProxyBridge()
clientEp.registerBridge(real, asDefault=True)
mainEp.registerBridge(proxy, asDefault=True)
await proxy.requestInitialize(ScrcpyInitParams(serial="..."))
```
