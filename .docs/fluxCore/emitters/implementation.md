# Implementation — OPEmitter

## File

`src/fluxCore/emitters/__outProcessEmitter.py`

## Design decisions

| Issue | Decision | Rationale |
|-------|----------|-----------|
| Parent task leaked | Store as `Task` created with `create_task` | Ensures the receiver is scheduled and can be cancelled |
| Drain on shutdown | Drain after Event is observed | Loop exits on Event; drain always runs afterward |
| Feeder thread leaks | `queue.close()` + `cancel_join_thread()` | Standard multiprocessing requirement after use |
| Fragile `.result()` | Never call `.result()` on cancelled parent task | Avoids blocking or exceptions in mixed sync/async stop paths |
| Attribute naming | Same names (`_inQueue`, `_outQueue`) on both sides | No collision; each process has its own instance after pickling |

## Shutdown sequence

```text
stop()
  ├─ set shutdownEvent
  ├─ AsyncProcess.stop()  → join / kill process
  ├─ cancel parent Task
  └─ close both queues
```

## Extension point

Subclasses override `work()` (child) and/or replace the print in `_receiver` with real handling (or subscribe to events).
