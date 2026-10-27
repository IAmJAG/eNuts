# Implementation Details

## 1. Architecture Overview

Transport is implemented. Higher layers (CommunicationManager, Bridge) are specified but not yet present as concrete classes.

```text
Application / domain code
        │
        ▼
Bridge (proposed)  ────────── commands / events / requests
        │
        ▼
CommunicationManager (proposed)
  inbound task · outbound task · correlation · handlers
        │
        ▼
IOQueue (implemented)
        │
        ▼
multiprocessing.Queue pair (implemented via createPair)
```

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/__IOQueue.py` | `.docs/jAGFx/IPC/IPC.md` | Queue adapter + `createPair` |
| `src/jAGFx/IPC/__message.py` | `.docs/jAGFx/IPC/IPC.md` | Message envelope |
| `src/jAGFx/types/interface/communication/__IOQueue.py` | `.docs/jAGFx/IPC/IPC.md` | `iIOQueue` contract |
| `src/jAGFx/types/interface/communication/__message.py` | `.docs/jAGFx/IPC/IPC.md` | `iMessage` contract |
| (proposed) CommunicationManager | `.docs/jAGFx/IPC/IPC.md` | Symmetric inbound/outbound + correlation |
| (proposed) Bridge | `.docs/jAGFx/IPC/IPC.md` | Entity ↔ IPC binding (real + proxy roles) |

## 3. Core Workflows & Data Flow

### Pair creation and orientation

```python
left, right = IOQueue.createPair()
# Process A
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
# Process B (receives right, left)
ioB = IOQueue(outboundQueue=right, inboundQueue=left)
```

### Send path (either side)

```text
Message(payload, correlationId?) → IOQueue.send → encode → JSON → outbound Queue.put
```

### Receive path (either side)

```text
inbound Queue.get → JSON → dictDecode → Message (or payload type) → manager dispatch / bridge
```

### Correlation

Either side may allocate a `correlationId` when sending a request. The peer’s response reuses that ID. Each manager keeps its own pending-request map; there is no cross-process shared correlator object.

## 4. Current code notes

- `IOQueue.receive` default timeout is `0.01` seconds.
- `Message` is not yet re-exported from `jAGFx.IPC.__init__` (only `IOQueue` is).
- Interface signatures for `iIOQueue` are aligned with the implementation (`createPair → tuple[Queue, Queue]`, `send(iMessage)`, `receive(timeout=...)`).
