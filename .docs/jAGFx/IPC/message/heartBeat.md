## Overview & Design Context
Heartbeat message used by out-of-process clients to report their liveness window to the parent.

* **Design Decision / Deviation Notes:** Payload is the beat window (seconds). Parent applies a small safety margin on expiry. Client sends at BEAT - fixed margin.

---

## Classes

### `Heartbeat`
- **Purpose:** Liveness signal from child to parent.
- **Methods:**
  - `__init__(beat=3.0, correlationId=None, messageId=None)` — sets ownerId to current process ident, payload=beat, isTerminal=True.

## Sample Usage

```python
from jAGFx.IPC.message import Heartbeat
hb = Heartbeat(beat=2.0)
# dispatched via ownDispatch / ProcessHost
```
