# eNuts IPC Architecture
## Mental Model, Technical Structure, and Usage

**Status:** Proposed architecture and illustrative usage  
**Scope:** Main process ↔ SCRCPY client process on Windows  
**Repository:** `IAmJAG/eNuts`, branch `development`

---

## 1. Purpose

This document describes the intended inter-process communication (IPC) architecture between the eNuts main process and a client process that owns a `SCRCPYEmitter`.

The design has one important rule:

> **The multiprocessing queues are the transport. `IOQueue` is a process-local adapter around those queues.**

Do not pass an `IOQueue` instance as the process argument. Create the underlying queue pair in the main process, pass the underlying queue references to the client process, and construct a separate `IOQueue` instance inside each process.

This document distinguishes existing repository behavior from proposed components and APIs. The example manager, bridge, proxy, message kinds, and lifecycle functions below are architectural examples, not claims that those exact APIs already exist.

## 2. Mental model

`IOQueue.createPair()` creates two `multiprocessing.Queue` objects and two oppositely oriented `IOQueue` adapters:

```python
@classmethod
def createPair(cls) -> tuple[IOQueue, IOQueue]:
    queueA, queueB = Queue(), Queue()
    return (cls(queueA, queueB), cls(queueB, queueA))
```

The constructor is `IOQueue(outboundQueue, inboundQueue)`. The first argument is used by `send()` and the second by `receive()`.

The queue topology is therefore:

```text
MAIN PROCESS                                  CLIENT PROCESS
-------------                                 --------------
mainIOQueue                                   clientIOQueue
  outbound = leftQueue                          outbound = rightQueue
  inbound  = rightQueue                         inbound  = leftQueue
        |                                             |
        +---- leftQueue ------------------------------+
        +----------------------------- rightQueue ----+
```

More explicitly:

- Main sends through `leftQueue`; client receives from `leftQueue`.
- Client sends through `rightQueue`; main receives from `rightQueue`.
- The main process owns a local `IOQueue` wrapper.
- The client process constructs its own local `IOQueue` wrapper.
- The wrappers are not shared Python objects.
- The two wrappers form one bidirectional logical connection.

The queues are created once. The endpoints are assigned in opposite order when the client constructs its adapter.

## 3. Responsibilities by layer

### 3.1 Transport layer — multiprocessing queues

Responsibilities:

- Carry encoded message data between processes.
- Provide independent inbound and outbound directions.
- Avoid carrying live application objects such as an emitter, sockets, or codec contexts.

The transport does not know about SCRCPY, the UI, or proxy behavior.

### 3.2 Message adapter — `IOQueue`

Existing implementation: `src/jAGFx/IPC/__IOQueue.py`.

Responsibilities:

- `send(message)`: call `message.encode()`, serialize the resulting dictionary to JSON, and enqueue it.
- `receive(timeout=None)`: wait for an inbound queue item, parse JSON, and call the project decoder to reconstruct the supported type.
- `createPair()`: create oppositely oriented queue adapters.
- `close()` and `cancelJoinThread()`: expose queue cleanup operations.

`receive()` defaults to a short timeout (currently `0.01` seconds), which allows a polling loop to periodically observe shutdown. The interface and implementation should remain aligned when the design is implemented.

### 3.3 Communication manager — one per process

**Proposed component.**

Each process creates its own manager and supplies its local `IOQueue` adapter. The manager should own:

- One inbound polling task.
- One outbound sender task and an event-loop-owned outbound queue.
- Message dispatch by message kind/type.
- Request/response correlation where a response is expected.
- Readiness, error, and shutdown signaling.
- Callback/handler registration.

The main-side manager and client-side manager have the same transport responsibilities, but their registered handlers differ.

The manager is process-local. It is not a central supervisor for many child processes.

### 3.4 Client emitter bridge

**Proposed component.**

The bridge lives in the client process. It subscribes to the real `SCRCPYEmitter` and translates emitter events into IPC messages.

It should not make the emitter itself responsible for IPC. This keeps the emitter focused on streaming and the bridge focused on transport adaptation.

### 3.5 Main-side emitter proxy

**Proposed component.**

The proxy lives in the main process. It exposes a local API and event surface that represents the remote emitter.

The proxy does not contain the actual emitter, sockets, codec context, or streaming loop. It translates supported operations into IPC commands and updates its local state when metadata, status, and other events arrive.

### 3.6 Client process entry point

The process entry point must be a module-level callable suitable for Windows `spawn`. Inside the child process it constructs the client-local `IOQueue`, initializes the manager, creates and initializes the emitter, wires the bridge, and runs the client asyncio loop.

Do not rely on a pre-created singleton instance being shared across the process boundary. Each process initializes its own process-local manager.

---

## 4. End-to-end architecture

```text
MAIN PROCESS
┌─────────────────────────────────────────────────────────┐
│ Application / UI                                        │
│       │                                                 │
│       ▼                                                 │
│ EmitterProxy                                             │
│       │ local command / local event                      │
│       ▼                                                 │
│ Main CommunicationManager                               │
│   ├── inbound poll task                                  │
│   ├── outbound sender task                               │
│   └── message dispatcher                                 │
│       │                                                 │
│       ▼                                                 │
│ mainIOQueue = IOQueue(leftQueue, rightQueue)             │
└───────┬───────────────────────────────┬─────────────────┘
        │ leftQueue                    │ rightQueue
        │ main → client                 │ client → main
        ▼                               ▲
================= PROCESS BOUNDARY =========================
        │                               │
        ▼                               │
┌───────┴───────────────────────────────┴─────────────────┐
│ CLIENT PROCESS                                           │
│ clientIOQueue = IOQueue(rightQueue, leftQueue)           │
│       │                                                 │
│ Client CommunicationManager                             │
│   ├── inbound poll task                                  │
│   ├── outbound sender task                               │
│   └── message dispatcher                                 │
│       │                          ▲                      │
│       ▼                          │                      │
│ Client command handlers      EmitterBridge               │
│       │                          ▲                      │
│       ▼                          │ emitter events         │
│ SCRCPYEmitter ────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

Each process runs its manager tasks on that process's own asyncio event loop. In the client, the manager and emitter can use the same loop. The main side should integrate with the application's existing loop, including `qasync` if applicable.

## 5. Inbound and outbound task model

Each process starts two concurrent transport tasks.

### Inbound path

```text
multiprocessing.Queue
    → IOQueue.receive()
    → JSON decoding and project type reconstruction
    → CommunicationManager dispatch
    → registered message handler
    → proxy update / command handler / application event
```

`IOQueue.receive()` is synchronous and waits briefly for a queue item. To keep an asyncio event loop responsive, a manager can call it through `asyncio.to_thread()`.

Illustrative pseudocode:

```python
async def pollInbound(self):
    while not self._stopping:
        try:
            message = await asyncio.to_thread(
                self._ioQueue.receive,
                0.01,
            )
        except Empty:
            continue

        await self._dispatch(message)
```

This snippet is a pattern, not a complete production implementation. The actual manager must handle decode errors, unexpected exceptions, shutdown, and task ownership. Cancelling a coroutine awaiting `asyncio.to_thread()` does not forcibly terminate a blocking function already running in a worker thread. Keep the receive timeout finite and make shutdown coordination explicit.

### Outbound path

```text
command or emitter callback
    → event-loop-owned asyncio.Queue
    → outbound sender task
    → IOQueue.send(message)
    → multiprocessing.Queue
```

The bridge callback should enqueue quickly rather than perform expensive serialization or block the streaming loop. A single sender task provides a clear place to handle ordering, send errors, and backpressure.

For an outbound worker, `IOQueue.send()` is synchronous. If sending becomes measurably blocking, it can be moved to a worker thread; keep the queue ownership and shutdown rules explicit.

---

## 6. Queue and process construction

### 6.1 Main process

The following example demonstrates the queue orientation and process argument order. It is not a complete application bootstrap.

```python
from multiprocessing import Process, Queue

# Create the underlying queues exactly once.
leftQueue = Queue()
rightQueue = Queue()

# The main adapter sends left and receives right.
mainIOQueue = IOQueue(
    outboundQueue=leftQueue,
    inboundQueue=rightQueue,
)

# Pass the underlying queues, not mainIOQueue.
clientProcess = Process(
    target=clientProcessEntry,
    args=(rightQueue, leftQueue, serial),
)
clientProcess.start()
```

### 6.2 Client process

The client entry point receives the queue references in the reverse order and creates its own adapter.

```python
def clientProcessEntry(rightQueue, leftQueue, serial):
    clientIOQueue = IOQueue(
        outboundQueue=rightQueue,
        inboundQueue=leftQueue,
    )
    asyncio.run(clientProcessMain(clientIOQueue, serial))
```

`clientProcessEntry` must be defined at module scope for Windows process spawning. Keep process startup under the application's guarded entry point where required:

```python
if __name__ == "__main__":
    main()
```

The precise application entry-point arrangement depends on the existing eNuts bootstrap.

### 6.3 Using `IOQueue.createPair()`

`createPair()` already returns two adapters, but if the adapter objects themselves are not the intended process arguments, use it only to obtain the underlying queues, or create the two queues explicitly as above. Do not pass either returned `IOQueue` wrapper to the child.

If using `createPair()` directly, the implementation must expose or otherwise obtain the underlying queue references in a deliberate way. Avoid reaching into `_in` and `_ou` from unrelated application code; a small documented factory/helper or a public pair-creation contract would be cleaner. The current `createPair()` return type is a pair of `IOQueue` instances, so it does not by itself provide a public API that returns just the queue objects.

This distinction is important: the desired process startup design uses the two underlying queues as process arguments, while each process owns a separately constructed adapter.

---

## 7. Emitter bridge and proxy

### 7.1 Event flow from client to main

The current `SCRCPYEmitter` raises:

- `ON_METADATA_UPDATE`, passing the emitter instance.
- `ON_FRAME`, passing the frame object.

The client-side bridge subscribes to these events and creates serializable IPC payloads.

```text
SCRCPYEmitter
  ├── ON_METADATA_UPDATE → EmitterBridge → metadata event message
  └── ON_FRAME           → EmitterBridge → frame event or frame descriptor
                                                │
                                                ▼
                                      Client manager outbound queue
                                                │
                                                ▼
                                           IOQueue.send()
```

The bridge should extract the required metadata from the emitter rather than attempt to serialize the emitter instance. Likewise, it should not assume a frame object is serializable merely because it is an event argument.

### 7.2 Command flow from main to client

```text
Application → EmitterProxy → Main manager → IOQueue
    → Client manager → command handler → SCRCPYEmitter
```

Example command mapping:

| Proxy operation | Illustrative message kind | Client handler |
|---|---|---|
| Initialize | `EMITTER_INITIALIZE` | Await emitter initialization |
| Start | `EMITTER_START` | Start emitter service |
| Stop | `EMITTER_STOP` | Stop emitter service |
| Readiness | `CLIENT_READY` | Mark proxy ready |
| Failure | `CLIENT_ERROR` | Mark proxy failed and expose error |
| Metadata changed | `EMITTER_METADATA` | Update proxy metadata |
| Frame received | `EMITTER_FRAME` | Deliver frame data or resolve its descriptor |

These names are illustrative protocol names. Define a typed message contract and use the project's `Message`/serializer conventions in the implementation.

### 7.3 Commands, responses, and events

Keep these concepts separate:

- **Command:** requests an operation.
- **Response/acknowledgement:** reports success or failure of a requested operation.
- **Event:** announces a state change or occurrence, such as updated metadata or a new frame.

Where a command expects a response, use the existing message correlation ID mechanism to associate the response with its request. Do not treat the mere successful enqueue of a command as proof that the client completed it.

---

## 8. Startup sequence

Recommended lifecycle:

1. Main creates the underlying left and right queues.
2. Main constructs its local `IOQueue` adapter.
3. Main creates its process-local manager and starts inbound/outbound tasks on its running event loop.
4. Main starts the client process, passing the underlying queues in reversed order and the required configuration.
5. Client constructs its own `IOQueue` adapter and its own manager.
6. Client starts inbound/outbound communication tasks.
7. Client creates `SCRCPYEmitter` and awaits `initialize()`.
8. Client subscribes the bridge to `ON_METADATA_UPDATE` and `ON_FRAME`.
9. Client sends `CLIENT_READY` only after communication setup and emitter initialization succeed.
10. Main receives readiness and marks its proxy as ready.
11. Client starts the emitter service and streams events.

The implementation should define whether the emitter starts just before or just after the ready message. Choose one ordering and make its meaning explicit. A useful contract is that `CLIENT_READY` means the client has initialized the emitter and is ready to accept start commands; the main then sends `EMITTER_START`.

### Initialization failure

If initialization fails:

- Client reports a structured error if the IPC path is operational.
- Client performs local cleanup.
- Main marks the proxy as failed rather than waiting indefinitely.
- The process exit code and process status remain available as a secondary failure signal.

A readiness timeout on the main side is also advisable.

---

## 9. Shutdown sequence

Shutdown should follow dependency order:

1. Main requests client shutdown or signals the client lifecycle mechanism.
2. Client stops the emitter service and awaits its service task as appropriate.
3. Client detaches or disables emitter bridge callbacks so no new events are submitted.
4. Client stops accepting new outbound messages and applies the chosen drain/drop policy.
5. Both managers stop their inbound and outbound tasks.
6. Each process performs queue cleanup according to the agreed endpoint ownership contract.
7. Main joins the child process and checks its exit status.

Do not close shared queue handles from one side while the other side is still expected to use them. Define who closes each handle, when each process stops using it, and whether pending messages are drained or discarded.

---

## 10. Frame transport and backpressure

Metadata, lifecycle events, commands, and acknowledgements are suitable for the ordinary message channel.

Video frames need a separate performance decision. Serializing full pixel buffers through JSON can be expensive and can flood the IPC queue. Consider:

- Sending metadata and frame descriptors over `IOQueue`.
- Keeping pixel bytes in shared memory or a dedicated binary transport.
- Including a frame ID, dimensions, pixel format, timestamp, and buffer reference in the descriptor.
- Defining buffer ownership and when a frame buffer can be reused.
- Using bounded queues and an explicit drop policy for stale frames.

For a live preview, dropping old frames may be better than letting the queue grow without bound. For recording or lossless processing, the policy may differ.

Do not send a raw memory address as a cross-process buffer reference. Use a transport mechanism with an explicit shared-memory handle/name and a lifetime protocol.

---

## 11. Process-local singleton behavior

If `CommunicationManager` uses the project's `SingletonC` decorator, initialize it independently inside each process.

The intended arrangement is:

```text
Main process:
    main manager singleton → mainIOQueue

Client process:
    client manager singleton → clientIOQueue
```

The singleton is process-local. It does not make the main manager instance available inside the child. Avoid constructing the manager in the parent and assuming that instance is the child's manager.

The manager's contract should also define whether it can be started only once per process, whether a stopped instance can restart, and how it rejects attempts to bind to a second queue endpoint.

---

## 12. Error handling and reliability checklist

Before treating the design as production-ready, verify the following:

- [ ] Queue orientation is correct: main outbound = left, client outbound = right.
- [ ] Only the underlying queue references cross the process creation boundary; each process constructs its own `IOQueue`.
- [ ] The process entry point is module-level and compatible with Windows `spawn`.
- [ ] Both inbound polling tasks and outbound sender tasks are started and supervised.
- [ ] The manager does not block the event loop on queue polling.
- [ ] Decode errors and unknown message kinds are handled explicitly.
- [ ] Requests expecting responses use correlation IDs.
- [ ] Readiness is acknowledged only after the documented initialization boundary.
- [ ] Client initialization failures are surfaced to the main process.
- [ ] UI updates are marshalled onto the UI thread.
- [ ] Frame transport has a bounded backpressure/drop policy.
- [ ] Shutdown does not close a queue while the peer still needs it.
- [ ] Child process termination and exit status are checked.
- [ ] Queue and manager ownership is documented and tested.

---

## 13. Suggested module responsibilities

Names below are proposed; align final filenames and exports with the project's naming conventions.

| Component | Responsibility |
|---|---|
| `jAGFx.IPC.IOQueue` | Existing queue adapter, JSON encoding/decoding, queue pair helper |
| `jAGFx.IPC.Message` | Existing message envelope and correlation identifier |
| `CommunicationManager` | Process-local polling, sending, dispatch, lifecycle |
| Typed message contracts | Commands, responses, events, readiness, errors |
| `EmitterBridge` | Client emitter events → IPC event messages |
| `EmitterProxy` | Main-side remote API and local event surface |
| Client process entry point | Construct client adapter and run the client event loop |
| Main bootstrap | Create queues, construct main adapter, launch client, supervise readiness/shutdown |

This division keeps generic IPC infrastructure in `jAGFx` and SCRCPY-specific adaptation near `fluxCore.emitters.scrcpy`.

---

## 14. Complete usage outline

The following is a compact integration outline. The named manager/proxy/bridge APIs are illustrative and must be implemented to match the actual message contracts.

### Main side

```python
# 1. Create transport queues.
leftQueue = Queue()
rightQueue = Queue()

# 2. Construct the main-local adapter.
mainIOQueue = IOQueue(leftQueue, rightQueue)

# 3. Start the main manager on the application's existing event loop.
mainManager = CommunicationManager(mainIOQueue)
await mainManager.startAsync()

# 4. Create a proxy backed by the main manager.
emitterProxy = EmitterProxy(mainManager)

# 5. Start the child with the queue references, not IOQueue.
clientProcess = Process(
    target=clientProcessEntry,
    args=(rightQueue, leftQueue, serial),
)
clientProcess.start()

# 6. Wait for CLIENT_READY with a timeout.
await emitterProxy.waitUntilReady(timeout=...)

# 7. Request streaming through the proxy.
await emitterProxy.start()

# 8. On application shutdown, request stop and clean up.
await emitterProxy.stop()
await mainManager.stopAsync()
clientProcess.join(timeout=...)
```

### Client side

```python
def clientProcessEntry(rightQueue, leftQueue, serial):
    clientIOQueue = IOQueue(rightQueue, leftQueue)
    asyncio.run(clientProcessMain(clientIOQueue, serial))


async def clientProcessMain(clientIOQueue, serial):
    manager = CommunicationManager(clientIOQueue)
    emitter = SCRCPYEmitter(serial=serial)
    bridge = EmitterBridge(emitter, manager)

    try:
        await manager.startAsync()

        await emitter.initialize()
        bridge.subscribe()

        await manager.publish(ClientReadyMessage())
        await manager.waitForShutdown()

    except Exception as err:
        await manager.tryPublish(ClientErrorMessage.fromException(err))
        raise

    finally:
        bridge.unsubscribe()
        # Stop the emitter if it was started; await its task if applicable.
        await manager.stopAsync()
```

This outline intentionally leaves the concrete message types, manager APIs, event registration, emitter start/stop details, and queue cleanup contract to the implementation. It communicates the integration order without inventing methods as though they already exist.

---

## 15. Existing repository behavior versus proposed design

### Existing behavior confirmed from the current code

- `IOQueue` takes outbound and inbound `multiprocessing.Queue` objects.
- `IOQueue.createPair()` creates two queues and returns two oppositely oriented `IOQueue` wrappers.
- `IOQueue.send()` encodes a message, serializes its dictionary to JSON, and enqueues it.
- `IOQueue.receive()` reads a queue item, parses JSON, and calls the project decoder.
- `Message` supports a message ID and optional correlation ID.
- `SCRCPYEmitter` raises `ON_FRAME` with a frame object and `ON_METADATA_UPDATE` with the emitter instance.
- `SCRCPYEmitter.initialize()` is asynchronous.
- `AsyncService.start()` is synchronous and schedules its service task on the current running event loop.

### Proposed work

- A process-local `CommunicationManager` with inbound and outbound tasks.
- A typed IPC command/response/event protocol.
- A client-side `EmitterBridge`.
- A main-side `EmitterProxy`.
- A readiness handshake and structured startup errors.
- Defined queue-handle ownership and shutdown behavior.
- A bounded frame transport strategy.

---

## 16. Final mental model

**The queue pair establishes the connection. Each process constructs its own `IOQueue`. Each process-local manager owns asynchronous message movement and dispatch. The client bridge translates the real emitter into IPC events. The main proxy translates IPC events and commands into a local emitter-like API.**

This keeps the IPC transport independent from SCRCPY, avoids passing an `IOQueue` wrapper across the process boundary, and lets the main application work with a local proxy while the actual emitter remains entirely inside the client process.
