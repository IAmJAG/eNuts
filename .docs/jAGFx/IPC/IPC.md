# eNuts IPC Architecture
## Mental Model, Technical Structure, and Usage

**Status:** Transport, Message, Endpoint, Bridge, control plane (Hello/Heartbeat)  
**Scope:** Symmetric inter-process communication between two processes  
**Repository:** `IAmJAG/eNuts`, branch `development`

---

## 1. Purpose

IPC connects two processes so domain entities in one process can be driven and observed from the other.

> **The multiprocessing queues are the transport. `IOQueue` is a process-local adapter.**

Do not pass an `IOQueue` across a process boundary.

---

## 2. Layers

| Layer | Role |
|-------|------|
| `IOQueue` | JSON encode/decode over `multiprocessing.Queue` |
| `Message` | Envelope: payload, correlationId, ownerId, isTerminal, … |
| `Endpoint` | Router by `ownerId` / default; outbound overload policy; peer alive map; drain on stop |
| `Bridge` | Correlation lifecycle (AMTT/DMTT); MRO type handlers; terminal policy |
| `ControlBridge` | Hello / HelloAck / Heartbeat → `Endpoint.markBridgeAlive` |

---

## 3. Routing

1. `ownerId is None` → default Bridge (`_defaultBridgeId` → `_bridges`)
2. `ownerId` in `_bridges` → that local Bridge
3. else drop

`_defaultBridgeId` is a **UUID** indexing `_bridges`, not a live Bridge reference.

---

## 4. Peer alive (no second registry)

```text
_bridges[localBridgeId]   → local Bridge instances
_bridgeAlive[peerBridgeId] → expiry (monotonic)   # peer ownerId / bridgeId
```

- Client sends `HelloMessage` / `HeartbeatMessage` with `ownerId = client.bridgeId`.
- Main `ControlBridge` calls `endpoint.markBridgeAlive(peerId, ttl)`.
- Main→peer application sends should check `endpoint.isBridgeAlive(peerBridgeId)` first.

No ClientSession / ClientRegistry. One id space: `bridgeId`.

---

## 5. Overload policy

`OverloadPolicy`: `UNBOUNDED` (default) | `BLOCK` | `DROP_NEW` | `DROP_OLD`  
Optional `outboundCapacity` applies when policy ≠ UNBOUNDED.

---

## 6. Shutdown

`await endpoint.stop(drainTimeout=1.0)`:

1. Set stopping  
2. Best-effort drain outbound  
3. Cancel tasks  
4. `IOQueue.close()` + `cancelJoinThread()`  
5. Clear local state  

---

## 7. Correlation (Bridge-owned)

```text
registerProcessor → AMTT + _processors
active timeout    → DMTT + _dprocessors
terminal          → immediate full removal
dormant timeout   → permanent removal
```

Type handlers: MRO walk, exact-type cache.

---

## 8. Control sequence

```text
Client                              Main
  | HelloMessage (ownerId=client.bridgeId)
  | ---------------------------------->|
  |                         markBridgeAlive
  | HelloAckMessage                    |
  | <----------------------------------|
  | HeartbeatMessage (periodic)        |
  | ---------------------------------->| refresh expiry
```

---

## 9. Domain bridges

Framework IPC is entity-agnostic. Domain message types and bridges live with the entity.

**First domain target:** SCRCPY emitter — see `.docs/fluxCore/emitters/scrcpy/implementationPlan.md` (Phase A emitter events done; messages/bridge pending under `src/fluxCore/emitters/scrcpy/`).

---

## 10. Public exports

```python
from jAGFx.IPC import (
    IOQueue, Message, Endpoint, Bridge, OverloadPolicy,
    ControlBridge, HelloMessage, HelloAckMessage, HeartbeatMessage,
)
```
