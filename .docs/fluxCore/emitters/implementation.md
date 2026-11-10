# Implementation — OPEmitter

## File

`src/fluxCore/emitters/__outProcessEmitter.py`

## Design decisions

| Issue | Decision | Rationale |
|-------|----------|-----------|
| Process started before loop check | Call `get_running_loop()` before `super().start()` | Failed start must not leave an orphaned child |
| Already-exited process raised in stop | `_reapProcess*` checks alive state; cleanup always in `finally` | Cooperative exit must not skip parent resource cleanup |
| Start failure leaked queues | Assign queues before `super().start()`; close on exception | Exception-safe allocation |
| `stop()` closed queues too early | Override `stopAsync`; `stop()` delegates to it when a loop exists | Queues stay open until the process has exited |
| Hard cancel skipped drain | Move `_drainQueue` into `_receiver` `finally` | Drain runs on normal exit and on cancellation |
| Feeder thread leaks | `queue.close()` + `cancel_join_thread()` | Standard multiprocessing requirement after use |

## Shutdown sequence

```text
stop() / stopAsync()
  ├─ set shutdownEvent (if process exists)
  ├─ if already exited: close process handle
  ├─ else: await/join process exit
  ├─ finally: cancel + await parent receiver
  └─ finally: close both queues
```

## Extension point

Subclasses override `work()` (child) and/or replace the print in `_receiver` with real handling (or subscribe to events).
