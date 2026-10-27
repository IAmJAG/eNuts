# eNuts IPC Architecture
## Mental Model, Technical Structure, and Usage

**Status:** Transport implemented; Endpoint and Bridge layers proposed  
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

The architecture is entity-agnostic. Concrete resources (e.g. SCRCPY) are examples of bridges, not the center of the design.

All IPC message traffic is **async**. There is no cross-process call that blocks for an immediate reply. A reply is always another message on the channel. Synchronous results exist only for local (same-process) calls.

---

## 2. Queue topology and `createPair`

`IOQueue.createPair()` returns the two underlying queues only:

```python
@classmethod
def createPair(cls) -> tuple[Queue, Queue]:
    return Queue(), Queue()
```

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

Wrappers are never shared. Only the queue objects cross the boundary.

---

## 3. Layers

### 3.1 Transport — `multiprocessing.Queue`

Carries encoded data. No application objects. Direction-independent pair.

### 3.2 Adapter — `IOQueue` (implemented)

`src/jAGFx/IPC/__IOQueue.py`

| Method | Behavior |
|--------|----------|
| `createPair()` | `(Queue, Queue)` |
| `send(message)` | encode → JSON → outbound `put` |
| `receive(timeout=None)` | inbound `get` → JSON → `dictDecode` (default `0.01`) |
| `close()` / `cancelJoinThread()` | cleanup |

### 3.3 Envelope — `Message` (implemented; fields to extend)

`src/jAGFx/IPC/__message.py`

| Field | Role |
|-------|------|
| `payload` | `iSerializable` body |
| `messageId` | Unique id for this message |
| `correlationId` | Conversation id |
| `timestamp` | Sortable creation/send time (wall-clock UTC or equivalent chronologically ordered value) |
| `isTerminal` | If true, this message ends the correlation after unmap |

**Kinds (logical):**

- **Command** — ask for an operation. **Request** is a subtype of command (no Future API; reply is just another message).
- **Response** — follows a command/request via `correlationId`.
- **Event** — unsolicited state change.

### 3.4 Endpoint (proposed) — `jAGFx.IPC.Endpoint`

One per process. Owns:

- Local `IOQueue`
- Inbound poll task and outbound sender task
- Kind → bridge dispatch for new conversations
- Correlation map: `correlationId → bridge`
- Bridge registration: `registerBridge` / `unregisterBridge`
- Public async push: `await endpoint.send(message)`

Does not own domain logic. Does not expose a blocking request/Future API; request is a command subtype handled with ordinary messages and optional processors on the bridge.

### 3.5 Bridge (proposed)

Binds one domain entity (real or proxy) to the endpoint.

- Exposes **message handlers** (kind/payload → callable) for new inbound conversations.
- On register, receives the endpoint and may call `await endpoint.send(...)`.
- Maintains `correlationId → processor` for ongoing conversations (custom or default for that message type).
- Owner side: real entity. Peer side: proxy surface. Same component concept.

Multiple bridges may share one endpoint; kind conflicts are rejected at registration.

---

## 4. Simple diagram

```text
PROCESS A                         PROCESS B
─────────                         ─────────
Bridge(s)                         Bridge(s)
   │ handlers + send                 │ handlers + send
   ▼                                 ▼
Endpoint                          Endpoint
   correlationId → bridge            correlationId → bridge
   inbound / outbound                inbound / outbound
   │                                 │
   ▼                                 ▼
IOQueue(left, right)              IOQueue(right, left)
   │                                 │
   └──────── process boundary ───────┘
```

---

## 5. Correlation system

### Two-level maps

```text
Endpoint:  correlationId → Bridge
Bridge:    correlationId → processor (callable)
```

Endpoint routes multi-bridge traffic. Bridge runs the domain-specific follow-up.

### Terminal flag

`isTerminal=True` means this message ends the conversation for that `correlationId`.

**Send path (locked):**

1. If **not** terminal: register (bridge processor + endpoint → bridge), then push.
2. If **terminal**:  
   - endpoint removes `correlationId → bridge` if present;  
   - bridge removes `correlationId → processor` if present;  
   - **then** the message is still pushed outbound.

**Register only if not terminal.**

**Receive path:** resolve bridge (by correlation id, else by kind), deliver message, then if terminal unmap if present (same “if exists” rule).

Either side may terminate. Any kind (command/request, response, event) may set `isTerminal`.

### Lifecycle summary

```text
Non-terminal send:  register → await send
Terminal send:      unmap if present → await send

Non-terminal receive: resolve → deliver (bridge may register if continuing)
Terminal receive:     resolve → deliver → unmap if present
```

### Async only

`await endpoint.send(message)` enqueues and returns. Replies arrive later as inbound messages. No IPC path returns a synchronous result. Local same-process calls remain ordinary method calls outside this channel.

---

## 6. Bridge registration

```text
endpoint.registerBridge(bridge)
  → bridge supplies messageHandlers
  → endpoint stores kind → bridge
  → bridge.attachEndpoint(endpoint)   # bridge may await endpoint.send

endpoint.unregisterBridge(bridge)
  → drop kind bindings and any correlations owned by that bridge
  → bridge.detachEndpoint()
```

Outbound from a bridge always goes through the endpoint public API, never through `IOQueue` directly.

---

## 7. Inbound / outbound tasks

**Inbound:** `IOQueue.receive` via `asyncio.to_thread` (finite timeout) → decode → dispatch by correlation or kind → bridge.

**Outbound:** bridge/application → `await endpoint.send` → event-loop queue → sender task → `IOQueue.send` → process queue.

Finite receive timeouts are required so shutdown can be observed.

---

## 8. Process construction

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
endpoint = Endpoint(ioA)
await endpoint.start()
# register bridges…

Process(target=processEntry, args=(right, left, config)).start()
```

```python
def processEntry(right, left, config):  # module-level, spawn-safe
    ioB = IOQueue(outboundQueue=right, inboundQueue=left)
    asyncio.run(processMain(ioB, config))
```

---

## 9. Startup / shutdown (transport)

**Startup:** create queues → local Endpoint + start tasks → spawn peer with reversed queues → peer Endpoint + bridges → optional readiness messages → traffic.

**Shutdown:** signal peer → bridges detach → endpoints stop tasks (explicit drain/drop) → close queues per ownership contract → join process.

Do not close a queue one side still uses.

---

## 10. Heavy payloads

Control, metadata, and small events use `IOQueue`. Large binaries should use descriptors over IPC plus shared memory (or equivalent) with an explicit lifetime protocol—not JSON pixel dumps.

---

## 11. Existing vs proposed

| Component | Status |
|-----------|--------|
| Queue pair + `IOQueue.createPair() → (Queue, Queue)` | Exists |
| `Message` (payload, messageId, correlationId) | Exists; add `timestamp`, `isTerminal` |
| `Endpoint` (`jAGFx.IPC`) | Proposed |
| `Bridge` + registration | Proposed |
| Correlation maps + terminal lifecycle | Proposed |
| Shared-memory / binary path for large payloads | Proposed |

---

## 12. Final mental model

**Queue pair = connection.**  
**Each process builds its own `IOQueue` and one `Endpoint`.**  
**Bridges register on the endpoint, expose handlers, and `await endpoint.send`.**  
**Correlation is two-level (endpoint → bridge, bridge → processor); terminal messages unmap then still flow.**  
**Request is a command subtype; all IPC is async; no cross-process immediate result.**
