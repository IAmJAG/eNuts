# eNuts IPC Architecture
## Mental Model, Technical Structure, and Usage

**Status:** Transport, Message, Endpoint, and Bridge base implemented  
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

The architecture is entity-agnostic. Concrete resources are examples of bridges, not the center of the design.

All IPC message traffic is **async**. There is no cross-process call that blocks for an immediate reply. A reply is always another message on the channel. Synchronous results exist only for local (same-process) calls.

---

## 2. Queue topology and `createPair`

```python
left, right = IOQueue.createPair()

ioA = IOQueue(outboundQueue=left,  inboundQueue=right)  # Process A
ioB = IOQueue(outboundQueue=right, inboundQueue=left)  # Process B
```

```text
PROCESS A                                         PROCESS B
-------------                                     -------------
IOQueue                                           IOQueue
  outbound = left                                   outbound = right
  inbound  = right                                  inbound  = left
        |                                                 |
        +---- left  (A → B) ------------------------------+
        +----------------------------- right (B → A) ----+
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
| `correlationId` | Conversation id |
| `timestamp` | Epoch seconds (float), chronologically sortable |
| `isTerminal` | Ends correlation after unmap |

Request is a subtype of command (logical). No Future API on Endpoint.

### 3.4 Endpoint — `jAGFx.IPC.Endpoint`

`src/jAGFx/IPC/__endpoint.py`

- Owns local `IOQueue`, inbound/outbound tasks
- `await send(message)` — if terminal, unmap then enqueue
- `registerBridge` / `unregisterBridge`
- `bindCorrelation` / `unbindCorrelation`
- Maps: message type → bridge, correlationId → bridge

### 3.5 Bridge — `jAGFx.IPC.Bridge`

`src/jAGFx/IPC/__bridge.py`

- `messageHandlers` (message **type** → callable)
- `attachEndpoint` / `detachEndpoint`
- `registerProcessor` / `unregisterProcessor`
- `handleMessage` (processor else type handler)
- `await send(message)` via attached endpoint

---

## 4. Simple diagram

```text
PROCESS A                              PROCESS B
─────────                              ─────────

  Bridge(s)                              Bridge(s)
     │                                      │
     │  handlers + await send               │  handlers + await send
     ▼                                      ▼
  Endpoint                               Endpoint
     correlationId → bridge                 correlationId → bridge
     inbound / outbound                     inbound / outbound
     │                                      │
     ▼                                      ▼
  IOQueue(left, right)                   IOQueue(right, left)
     │                                      │
     └────────── process boundary ──────────┘
```

---

## 5. Correlation and terminal lifecycle

```text
Endpoint:  correlationId → Bridge
Bridge:    correlationId → processor
```

**Send**

- Non-terminal: bridge registers processor + `endpoint.bindCorrelation`, then `await send`.
- Terminal: endpoint unmaps correlation (and bridge processor) if present, **then** pushes.

**Receive**

- Resolve by correlationId else by message type → `bridge.handleMessage`.
- If terminal: unmap if present after deliver.

Register correlation only when not terminal.

---

## 6. Process construction

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
endpoint = Endpoint(ioA)
await endpoint.start()
endpoint.registerBridge(someBridge)

Process(target=processEntry, args=(right, left, config)).start()
```

```python
def processEntry(right, left, config):  # module-level, spawn-safe
    ioB = IOQueue(outboundQueue=right, inboundQueue=left)
    asyncio.run(processMain(ioB, config))
```

---

## 7. Existing components

| Component | Status |
|-----------|--------|
| `IOQueue` + `createPair() → (Queue, Queue)` | Implemented |
| `Message` (+ timestamp, isTerminal) | Implemented |
| `Endpoint` | Implemented |
| `Bridge` base | Implemented |
| Domain messages / bridges | **First target: SCRCPY** — see `.docs/fluxCore/emitters/scrcpy/implementationPlan.md` |
| Shared-memory / large binary path | Not in scope yet |

Domain message types and footprints live under `src/fluxCore/emitters/scrcpy/`, not under `jAGFx.IPC`.

---

## 8. Final mental model

**Queue pair = connection.**  
**Each process builds its own `IOQueue` and one `Endpoint`.**  
**Bridges register on the endpoint, expose handlers, and `await endpoint.send`.**  
**Correlation is two-level; terminal messages unmap then still flow.**  
**Request ⊂ command; all IPC is async.**
