# eNuts IPC Architecture
## Mental Model, Technical Structure, and Usage

**Status:** Transport, Message, Endpoint, and Bridge base implemented (IPC-01 lifecycle remediation applied)  
**Scope:** Symmetric inter-process communication between two processes  
**Repository:** `IAmJAG/eNuts`, branch `development`

---

## 1. Purpose

IPC connects two processes so that domain entities living in one process can be driven and observed from the other.

Core rule:

> **The multiprocessing queues are the transport. `IOQueue` is a process-local adapter around those queues.**

Do not pass an `IOQueue` instance across a process boundary. Create the underlying queue pair once, pass the queue references, and construct a separate `IOQueue` inside each process.

The design is **symmetric**:

- Both processes run the same `Endpoint` type (`jAGFx.IPC`).
- Both support inbound and outbound traffic.
- Both can originate messages and allocate correlation IDs.
- Both register bridges and handlers.
- The only structural difference is queue orientation.

A **Bridge** binds a domain entity to the local endpoint. On the owner process it drives the real entity; on the peer it acts as a proxy. The machinery is the same.

All IPC message traffic is **async**. There is no cross-process call that blocks for an immediate reply. A reply is always another message on the channel.

---

## 2. Queue topology and `createPair`

```python
left, right = IOQueue.createPair()

ioA = IOQueue(outboundQueue=left,  inboundQueue=right)  # Process A
ioB = IOQueue(outboundQueue=right, inboundQueue=left)  # Process B
```

---

## 3. Layers

### 3.1 Transport — `multiprocessing.Queue`

Carries encoded data. No application objects.

### 3.2 Adapter — `IOQueue`

`src/jAGFx/IPC/__IOQueue.py` — `createPair()`, `send`, `receive`, `close`.

### 3.3 Envelope — `Message`

`src/jAGFx/IPC/__message.py`

| Field | Role |
|-------|------|
| `payload` | `iSerializable` body |
| `messageId` | Unique id |
| `correlationId` | Conversation id (always present) |
| `ownerId` | Optional Bridge ID for routing (`None` → default Bridge) |
| `timestamp` | Epoch seconds (float) |
| `isTerminal` | Ends correlation (Bridge policy) |

### 3.4 Endpoint — pure router

`src/jAGFx/IPC/__endpoint.py`

- Owns local `IOQueue`, inbound/outbound tasks
- `registerBridge(bridge, asDefault=False)` / `unregisterBridge`
- Routes solely by `message.ownerId` → `_bridges[ownerId]` or `_defaultBridgeId`
- **No** correlation-to-Bridge map
- **No** message-type Bridge selection

`_defaultBridgeId` is a `UUID | None` that indexes into `_bridges`.

### 3.5 Bridge — correlation owner

`src/jAGFx/IPC/__bridge.py`

- `bridgeId: UUID` (identity; used as `ownerId` on outbound messages)
- `messageHandlers` (message type → callable) — used *after* Bridge selection
- AMTT / DMTT + active/dormant processor maps
- Terminal policy: immediate full cleanup
- Active → dormant → permanent expiry via `AsyncService` timeout loops
- `attachEndpoint` / `detachEndpoint` start/stop timeout services

---

## 4. Routing rules

1. `ownerId is None` → default Bridge (`_defaultBridgeId`)
2. `ownerId` registered → that Bridge
3. unknown non-null `ownerId` → drop (routing error)

Message type never overrides Bridge selection.

---

## 5. Correlation lifecycle (Bridge-owned)

```text
registerProcessor → AMTT + _processors   (active)
active timeout    → DMTT + _dprocessors  (dormant)
terminal message  → immediate full removal
dormant timeout   → permanent removal
```

Validation of correlation existence uses the trackers (`amtt` / `dmtt`), not the processor maps alone.

---

## 6. Process construction

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
endpoint = Endpoint(ioA)
await endpoint.start()
endpoint.registerBridge(someBridge, asDefault=True)

Process(target=processEntry, args=(right, left, config)).start()
```

---

## 7. Final mental model

**Queue pair = connection.**  
**Each process builds its own `IOQueue` and one `Endpoint`.**  
**Endpoint routes by Bridge ID (`ownerId`) or default.**  
**Bridge owns all correlation state and lifecycle policies.**  
**Terminal = immediate cleanup on the Bridge.**  
**All IPC is async.**
