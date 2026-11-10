# Implementation — OPEmitter

## File

`src/fluxCore/emitters/__outProcessEmitter.py`

## Ownership

| Responsibility | Owner |
|----------------|--------|
| Process signal / join / kill / handle close | `AsyncProcess` |
| `ON_STOPPING` / `ON_STOPPED` | `AsyncProcess` |
| Parent receiver cancel + await | `OPEmitter` |
| Queue close | `OPEmitter` |
| Shutdown task retention | `OPEmitter` |

## Design decisions

| Issue | Decision | Rationale |
|-------|----------|-----------|
| Race on already-exited process | `AsyncProcess._assertStopReady` only rejects a missing handle | An exited handle is still reapable; no second lifecycle in OPEmitter |
| Duplicated reaping | `stopAsync` / no-loop `stop` call `super()` then cleanup in `finally` | Single source of truth for process lifecycle and events |
| Untracked shutdown task | Retain `_stopTask`; coalesce if already running; surface failures via loop exception handler + `waitStopped()` | Failures are observable; concurrent stops do not stack |
| Process started before loop check | Call `get_running_loop()` before `super().start()` | Failed start must not leave an orphaned child |
| Start failure leaked queues | Assign queues before `super().start()`; close on exception | Exception-safe allocation |
| Hard cancel skipped drain | Move `_drainQueue` into `_receiver` `finally` | Drain runs on normal exit and on cancellation |

## Shutdown sequence

```text
stop() / stopAsync()
  ├─ AsyncProcess.stop*  → ON_STOPPING, signal, join/kill, close handle, ON_STOPPED
  └─ finally: cancel + await parent receiver, close queues
```

## Extension point

Subclasses override `work()` (child) and/or replace the print in `_receiver` with real handling (or subscribe to events).
