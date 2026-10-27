# eNuts IPC Architecture
## Mental Model, Technical Structure, and Usage

**Status:** Transport implemented; manager and bridge layers proposed  
**Scope:** Symmetric inter-process communication between two processes  
**Repository:** `IAmJAG/eNuts`, branch `development`

---

## 1. Purpose

This document describes the inter-process communication (IPC) architecture used when one process needs to manage an entity that lives in another process.

Core rule:

> **The multiprocessing queues are the transport. `IOQueue` is a process-local adapter around those queues.**

Do not pass an `IOQueue` instance across a process boundary. Create the underlying queue pair once, pass the queue references, and construct a separate `IOQueue` inside each process.

The design is **symmetric**:

- Both processes run the same kind of `CommunicationManager`.
- Both support inbound and outbound traffic.
- Both can originate requests and generate correlation IDs.
- Both can register command handlers.
- The only structural difference between the two ends is the orientation of the queue pair each adapter holds.

An entity that needs remote management (commands, events, request/response) is represented by a **Bridge**. On the process that owns the real object the bridge talks to the real entity; on the other process the same bridge concept appears as a proxy surface. The machinery is the same; only which side holds the real object differs.

SCRCPY / emitters are one example of such an entity. The architecture is not designed around them.

---

## 2. Queue topology and `createPair`

`IOQueue.createPair()` returns the two underlying queues only:

```python
@classmethod
def createPair(cls) -> tuple[Queue, Queue]:
    return Queue(), Queue()
```

Each process then builds its own adapter:

```python
left, right = IOQueue.createPair()

# Process A (local outbound = left)
localIO  = IOQueue(outboundQueue=left,  inboundQueue=right)

# Process B receives (right, left) and builds the reverse adapter
remoteIO = IOQueue(outboundQueue=right, inboundQueue=left)
```

```text
PROCESS A                                         PROCESS B
-------------                                     -------------
localIO                                           remoteIO
  outbound = left                                   outbound = right
  inbound  = right                                  inbound  = left
        |                                                 |
        +---- left  (A → B) ------------------------------+
        +----------------------------- right (B → A) ----+
```

- Process A sends on `left`; Process B receives on `left`.
- Process B sends on `right`; Process A receives on `right`.
- Wrappers are never shared. Only the queue objects cross the boundary.

---

## 3. Layers

### 3.1 Transport — `multiprocessing.Queue`

- Carries encoded message data.
- Independent directions (no shared application objects).
- Knows nothing about managers, bridges, or domain entities.

### 3.2 Adapter — `IOQueue` (implemented)

Location: `src/jAGFx/IPC/__IOQueue.py`

| Method | Behavior |
|--------|----------|
| `createPair()` | Returns `(Queue, Queue)` |
| `send(message)` | `message.encode()` → JSON → outbound `put` |
| `receive(timeout=None)` | inbound `get` → JSON → project `dictDecode` (default timeout `0.01`) |
| `close()` / `cancelJoinThread()` | Queue cleanup |

Constructor: `IOQueue(outboundQueue, inboundQueue)`.

### 3.3 Envelope — `Message` (implemented)

Location: `src/jAGFx/IPC/__message.py`

- `payload: iSerializable`
- `messageId: UUID` (always new)
- `correlationId: UUID | None` (optional; defaults to a new UUID)

Either side may originate a message and supply its own correlation ID for request/response matching.

### 3.4 CommunicationManager (proposed, identical on both sides)

One manager per process. Responsibilities:

- Own the process-local `IOQueue`.
- Inbound polling task (`receive` via `asyncio.to_thread` with finite timeout).
- Outbound sender task fed by an event-loop `asyncio.Queue`.
- Dispatch by payload / message kind.
- Request/response correlation map (both directions).
- Handler registration (commands, events, responses).
- Start / stop / readiness / error signaling for the transport itself.

There is no “main manager” vs “client manager” type. The same class is instantiated in each process; only the `IOQueue` orientation differs.

### 3.5 Bridge (proposed, generalized)

A **Bridge** is the component that binds a domain entity to the IPC channel.

- It registers command handlers with the local `CommunicationManager`.
- It translates entity events into outbound IPC messages.
- It translates inbound IPC messages into entity operations or proxy state updates.
- It may originate requests and wait on correlation IDs.

Two complementary roles of the same concept:

| Side | Role | What it holds |
|------|------|---------------|
| Owner process | Real bridge | The real entity + handlers that drive it |
| Peer process | Proxy bridge | Local API / events that mirror the entity; no real resources |

The bridge is the place where “command handler” and “event adapter” meet. It is not limited to one entity type; any entity that exposes commands and events can have a bridge.

---

## 4. End-to-end view (symmetric)

```text
PROCESS A                                              PROCESS B
┌────────────────────────────────┐                     ┌────────────────────────────────┐
│ Application / other bridges    │                     │ Application / other bridges    │
│         │                      │                     │         │                      │
│         ▼                      │                     │         ▼                      │
│ Bridge (proxy or real)         │                     │ Bridge (real or proxy)         │
│   commands / events / requests │                     │   commands / events / requests │
│         │                      │                     │         │                      │
│         ▼                      │                     │         ▼                      │
│ CommunicationManager           │                     │ CommunicationManager           │
│   inbound task                 │                     │   inbound task                 │
│   outbound task                │                     │   outbound task                 │
│   correlation map              │                     │   correlation map              │
│   handlers                     │                     │   handlers                     │
│         │                      │                     │         │                      │
│         ▼                      │                     │         ▼                      │
│ IOQueue(left, right)           │                     │ IOQueue(right, left)           │
└─────────┬──────────────────────┘                     └──────────┬─────────────────────┘
          │ left (A→B)                                            │
          │ right (B→A)                                           │
          └──────────────────── process boundary ─────────────────┘
```

Both managers are independently responsible for their own inbound and outbound paths. Either side may send a request; the other side’s handler answers using the same `correlationId`.

---

## 5. Inbound and outbound task model

Identical on both sides.

### Inbound

```text
Queue → IOQueue.receive() → decode → CommunicationManager.dispatch
      → registered handler / bridge / correlation waiter
```

Pattern (illustrative):

```python
async def pollInbound(self):
    while not self._stopping:
        try:
            message = await asyncio.to_thread(self._ioQueue.receive, 0.01)
        except Empty:
            continue
        await self._dispatch(message)
```

Finite timeouts are required so shutdown can be observed. Cancelling a coroutine that is awaiting `to_thread` does not abort a blocking `get` already running in a worker thread.

### Outbound

```text
bridge / handler / application
    → asyncio.Queue (event-loop owned)
    → outbound sender task
    → IOQueue.send(message)
    → multiprocessing.Queue
```

Bridge callbacks should enqueue quickly; serialization and send stay on the outbound task (or a worker thread if measured as blocking).

---

## 6. Process construction

```python
# Process A
left, right = IOQueue.createPair()
localIO = IOQueue(outboundQueue=left, inboundQueue=right)
manager = CommunicationManager(localIO)
await manager.startAsync()

process = Process(
    target=processEntry,          # module-level, Windows-spawn safe
    args=(right, left, config),
)
process.start()
```

```python
# Process B entry (module scope)
def processEntry(right, left, config):
    remoteIO = IOQueue(outboundQueue=right, inboundQueue=left)
    asyncio.run(processMain(remoteIO, config))
```

Pass only the queue objects. Each process constructs its own `IOQueue` and `CommunicationManager`.

---

## 7. Commands, responses, and events

Keep the three distinct:

- **Command** — request an operation (may expect a response).
- **Response** — result of a command; matches via `correlationId`.
- **Event** — unsolicited state change or occurrence.

Either process may emit any of the three. Correlation is therefore a property of the manager on **both** sides, not a privilege of one “main” side.

---

## 8. Bridge responsibilities (general)

A bridge:

1. Registers the command set it accepts with the local manager.
2. Maps inbound commands onto the real entity (owner side) or onto local proxy state (peer side).
3. Subscribes to entity events (owner side) and publishes them as IPC events.
4. On the proxy side, exposes a local API and raises local events when IPC events arrive.
5. May issue requests and await correlated responses.

Multiple bridges can share one `CommunicationManager` by registering different message kinds / payload types.

---

## 9. Startup and shutdown (transport-level)

**Startup (typical)**

1. Process A creates queue pair and local `IOQueue` + manager; starts manager tasks.
2. Process A starts Process B, passing the reversed queue pair and config.
3. Process B builds its `IOQueue` + manager; starts manager tasks.
4. Each side that owns real entities constructs them and their bridges.
5. Optional readiness messages are exchanged so each side knows the peer is live.
6. Normal command / event traffic begins.

**Shutdown**

1. Signal the peer (explicit message and/or process lifecycle event).
2. Bridges stop accepting new work and detach from entities.
3. Managers stop inbound/outbound tasks (drain or drop policy is explicit).
4. Queues are closed according to an agreed ownership contract.
5. Process A joins Process B and inspects the exit status.

Do not close a queue handle from one side while the other still expects to use it.

---

## 10. Heavy payloads (e.g. frames, large buffers)

Control messages, metadata, and small events belong on the `IOQueue` channel.

Large binary payloads should not be JSON-serialized through the message queue. Prefer:

- descriptors over `IOQueue` (id, shape, format, timestamp, shared-memory name/handle),
- an explicit shared-memory or dedicated binary transport with a defined lifetime protocol,
- a bounded queue + drop policy when the traffic is live preview rather than lossless capture.

Never pass a raw process-local memory address as a cross-process reference.

---

## 11. Process-local lifetime

Managers and bridges are process-local. If a singleton decorator is used, it is still one instance **per process**. Do not construct a manager in the parent and assume the child sees the same object.

---

## 12. Existing vs proposed

| Component | Status |
|-----------|--------|
| `multiprocessing.Queue` pair | Exists |
| `IOQueue` + `createPair() → (Queue, Queue)` | Exists |
| `Message` (payload, messageId, correlationId) | Exists |
| Project serializer encode/decode | Exists |
| `CommunicationManager` (symmetric) | Proposed |
| Generalized `Bridge` (real + proxy roles) | Proposed |
| Typed command / response / event protocol | Proposed |
| Readiness / shutdown contracts | Proposed |
| Binary / shared-memory transport for large payloads | Proposed |

---

## 13. Final mental model

**Queue pair = connection.**  
**Each process builds its own `IOQueue`.**  
**Each process runs the same `CommunicationManager` (inbound, outbound, correlation, handlers).**  
**A Bridge attaches a domain entity to that manager—as the real object on one side and as a proxy on the other.**  
**Either side may originate commands, events, or correlated requests.**

The transport stays independent of any particular entity. SCRCPY (or any other remote resource) is just one bridge among others.
