# Implementation — OPEmitter

## File

`src/fluxCore/emitters/__outProcessEmitter.py`

## Design decisions

| Issue | Decision | Rationale |
|-------|----------|-----------|
| Parent task leaked | Store as `Task` created with `create_task` | Ensures the receiver is scheduled and can be cancelled |
| No drain on shutdown | Sentinel object + explicit drain | Guarantees both sides exit and leftover messages are discarded cleanly |
| Feeder thread leaks | `queue.close()` + `cancel_join_thread()` | Standard multiprocessing requirement after use |
| Race between Event and receiver | Set Event **and** inject sentinels | Covers both blocking `wait` and polling receivers |
| Fragile `.result()` | Never call `.result()` on cancelled parent task | Avoids blocking or exceptions in mixed sync/async stop paths |
| Queue ownership confusion | Store parent queues explicitly (`_parentInQueue`, `_parentOutQueue`) | Clear ownership after the swap performed for the child |

## Shutdown sequence

```text
stop()
  ├─ set shutdownEvent
  ├─ put sentinel → parentOutQueue (child in)
  ├─ put sentinel → parentInQueue (parent receiver)
  ├─ AsyncProcess.stop()  → join / kill process
  ├─ cancel parent Task
  └─ close both queues
```

## Extension point

Subclasses override `work()` (child) and/or replace the print in `_receiver` with real handling (or subscribe to events).
