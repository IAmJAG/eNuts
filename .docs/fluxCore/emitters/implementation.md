# Implementation — OPEmitter

## File

`src/fluxCore/emitters/__outProcessEmitter.py`

## Design decisions

| Issue | Decision | Rationale |
|-------|----------|-----------|
| Process started before loop check | Call `get_running_loop()` before `super().start()` | Failed start must not leave an orphaned child |
| `stop()` closed queues too early | Override `stopAsync`; `stop()` delegates to it when a loop exists | Queues stay open until the process has exited |
| `stopAsync` skipped OPEmitter cleanup | Both paths call the same finish + close sequence | Sync and async callers leave the same residual state |
| Hard cancel skipped drain | Move `_drainQueue` into `_receiver` `finally` | Drain runs on normal exit and on cancellation |
| Feeder thread leaks | `queue.close()` + `cancel_join_thread()` | Standard multiprocessing requirement after use |

## Shutdown sequence

```text
stop() / stopAsync()
  ├─ set shutdownEvent
  ├─ await process exit (join / kill)
  ├─ cancel + await parent receiver (hard cancel)
  └─ close both queues
```

## Extension point

Subclasses override `work()` (child) and/or replace the print in `_receiver` with real handling (or subscribe to events).
