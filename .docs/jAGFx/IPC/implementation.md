# Implementation Details

## 1. Architecture

```text
ControlBridge / domain Bridges
        │
     Endpoint  (_bridges, _defaultBridgeId, _bridgeAlive, overload, drain)
        │
     IOQueue
        │
  multiprocessing.Queue pair
```

## 2. Module map

| Source | Role |
|--------|------|
| `IPC/__endpoint.py` | Router, alive, overload, errors, stop drain |
| `IPC/__bridge.py` | Correlation + MRO handlers |
| `IPC/__overload.py` | `OverloadPolicy` |
| `IPC/control/__messages.py` | Hello, HelloAck, Heartbeat |
| `IPC/control/__bridge.py` | ControlBridge |
| `IPC/__IOQueue.py` | Transport adapter |
| `IPC/__message.py` | Envelope + ownerId |

## 3. Shutdown sequence

stop → drain outbound (deadline) → cancel tasks → ioQueue.close/cancelJoinThread → clear

## 4. Alive API

```python
endpoint.markBridgeAlive(peerBridgeId, ttlS)
endpoint.isBridgeAlive(peerBridgeId)
endpoint.sweepDeadBridges()
```

## 5. Overload

Configured at construction / via property. Capacity used when policy ≠ UNBOUNDED.
