# Implementation Details

## 1. Architecture Overview

```text
Bridge(s)  →  Endpoint  →  IOQueue  →  multiprocessing.Queue pair
```

Phases 1–4 of `implementationPlan.md` are implemented. Concrete domain bridges remain application work.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/__IOQueue.py` | `.docs/jAGFx/IPC/` | Queue adapter + `createPair` |
| `src/jAGFx/IPC/__message.py` | `.docs/jAGFx/IPC/` | Message envelope |
| `src/jAGFx/IPC/__endpoint.py` | `.docs/jAGFx/IPC/` | Endpoint |
| `src/jAGFx/IPC/__bridge.py` | `.docs/jAGFx/IPC/` | Bridge base |
| `src/jAGFx/types/interface/communication/` | `.docs/jAGFx/IPC/` | `iIOQueue`, `iMessage`, `iEndpoint`, `iBridge` |
| `.docs/jAGFx/IPC/implementationPlan.md` | — | Phased plan (1–4 done) |

## 3. Core workflows

### Pair + orientation

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
ioB = IOQueue(outboundQueue=right, inboundQueue=left)
```

### Send

```text
Non-terminal: bridge registerProcessor + endpoint.bindCorrelation → await send
Terminal:     endpoint unmap if present → await send (still pushed)
```

### Receive

```text
IOQueue.receive → decode → resolve bridge (correlationId or kind)
→ bridge.handleMessage → if isTerminal: unmap if present
```

### Kind resolution (provisional)

`getattr(payload, "kind", None)` if str, else `type(payload).__name__`.

## 4. Public exports

```python
from jAGFx.IPC import IOQueue, Message, Endpoint, Bridge
from jAGFx.types.interface.communication import iIOQueue, iMessage, iEndpoint, iBridge
```
