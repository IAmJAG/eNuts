# Implementation Details

## 1. Architecture Overview

```text
Bridge(s)  →  Endpoint  →  IOQueue  →  multiprocessing.Queue pair
```

Transport is implemented. `Endpoint` and `Bridge` follow the phased plan in `implementationPlan.md`.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/__IOQueue.py` | `.docs/jAGFx/IPC/` | Queue adapter + `createPair` |
| `src/jAGFx/IPC/__message.py` | `.docs/jAGFx/IPC/` | Message envelope |
| `src/jAGFx/IPC/__endpoint.py` | `.docs/jAGFx/IPC/` | Endpoint (proposed — Phase 2+) |
| `src/jAGFx/IPC/__bridge.py` | `.docs/jAGFx/IPC/` | Bridge base (proposed — Phase 3+) |
| `src/jAGFx/types/interface/communication/` | `.docs/jAGFx/IPC/` | `iIOQueue`, `iMessage`, `iEndpoint`, `iBridge` |
| `.docs/jAGFx/IPC/implementationPlan.md` | — | Phased build order and file-level changes |

## 3. Core workflows

### Pair + orientation

```python
left, right = IOQueue.createPair()
ioA = IOQueue(outboundQueue=left, inboundQueue=right)
ioB = IOQueue(outboundQueue=right, inboundQueue=left)
```

### Send / receive / correlation

See `IPC.md` and `implementationPlan.md` Phase 4 for terminal unmap-then-push and two-level maps.

## 4. Current code notes

- `IOQueue.receive` default timeout: `0.01` s.
- `Message` today: payload, correlationId, messageId — Phase 1 adds `timestamp`, `isTerminal`.
- `jAGFx.IPC.__init__` currently exports `IOQueue` only.
- `iIOQueue` matches implementation (`createPair → tuple[Queue, Queue]`, `send(iMessage)`, `receive(timeout=...)`).
