# Implementation Details

## 1. Architecture Overview

```text
Bridge(s)  →  Endpoint  →  IOQueue  →  multiprocessing.Queue pair
   │              │
   │              └─ routes by ownerId / defaultBridgeId (UUID)
   │
   └─ owns AMTT, DMTT, processors, terminal + timeout policies
```

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/__IOQueue.py` | `.docs/jAGFx/IPC/` | Queue adapter + `createPair` |
| `src/jAGFx/IPC/__message.py` | `.docs/jAGFx/IPC/` | Message envelope (+ ownerId) |
| `src/jAGFx/IPC/__endpoint.py` | `.docs/jAGFx/IPC/` | Pure Bridge-ID router |
| `src/jAGFx/IPC/__bridge.py` | `.docs/jAGFx/IPC/` | Correlation lifecycle owner |
| `src/jAGFx/types/interface/communication/` | `.docs/jAGFx/IPC/` | `iIOQueue`, `iMessage`, `iEndpoint`, `iBridge` |

## 3. Core workflows

### Pair + orientation

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
ioB = IOQueue(outboundQueue=right, inboundQueue=left)
```

### Registration

```python
endpoint.registerBridge(bridge, asDefault=True)  # _defaultBridgeId = bridge.bridgeId
endpoint.registerBridge(otherBridge)             # ownerId routing only
```

### Send

```text
bridge.send(message)
  → stamps message.ownerId = bridge.bridgeId (if unset)
  → endpoint.send → outbound queue
```

### Receive / route

```text
IOQueue.receive → decode
  → ownerId is None? → _bridges[_defaultBridgeId]
  → ownerId registered? → _bridges[ownerId]
  → else drop
  → bridge.handleMessage
       → processor (active then dormant) or type handler
       → if isTerminal: Bridge terminal policy (immediate full cleanup)
```

### Correlation lifecycle (Bridge)

```text
registerProcessor → amtt + _processors
active timeout    → dmtt + _dprocessors
terminal          → remove from all four collections
dormant timeout   → permanent removal
```

Timeout services use monotonic_ns elapsed accounting and AsyncService.wake / live throttle.

## 4. Public exports

```python
from jAGFx.IPC import IOQueue, Message, Endpoint, Bridge
from jAGFx.types.interface.communication import iIOQueue, iMessage, iEndpoint, iBridge
```
