# Implementation Details

## 1. Architecture Overview

```text
Bridge(s)  →  Endpoint  →  IOQueue  →  multiprocessing.Queue pair
```

Transport is implemented. `Endpoint` and `Bridge` are specified, not yet concrete classes.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/__IOQueue.py` | `.docs/jAGFx/IPC/` | Queue adapter + `createPair` |
| `src/jAGFx/IPC/__message.py` | `.docs/jAGFx/IPC/` | Message envelope (extend: timestamp, isTerminal) |
| `src/jAGFx/types/interface/communication/` | `.docs/jAGFx/IPC/` | `iIOQueue`, `iMessage` |
| (proposed) `src/jAGFx/IPC/` Endpoint | `.docs/jAGFx/IPC/` | Symmetric endpoint |
| (proposed) Bridge | `.docs/jAGFx/IPC/` | Entity binding + processors |

## 3. Core workflows

### Pair + orientation

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
ioB = IOQueue(outboundQueue=right, inboundQueue=left)
```

### Send

```text
Non-terminal: register correlation → await endpoint.send → outbound task → IOQueue.send
Terminal:     unmap if present     → await endpoint.send → outbound task → IOQueue.send
```

### Receive

```text
IOQueue.receive → decode → resolve bridge (correlationId or kind) → deliver
→ if isTerminal: unmap if present
```

### Correlation maps

```text
Endpoint._correlations: correlationId → Bridge
Bridge._processors:     correlationId → Callable
```

## 4. Current code notes

- `IOQueue.receive` default timeout: `0.01` s.
- `Message` today: payload, correlationId, messageId — still needs `timestamp` and `isTerminal`.
- `jAGFx.IPC.__init__` currently exports `IOQueue` only.
- `iIOQueue` signatures match implementation (`createPair → tuple[Queue, Queue]`, `send(iMessage)`, `receive(timeout=...)`).
