# OPEmitter

Out-of-process base emitter. Heavy work runs in a separate process while the parent (usually the UI loop) remains responsive.

## Purpose

Separate a heavy method/function into a different process than the main process. Provides bidirectional Queue IPC and a cooperative shutdown via a shared Event.

## Inheritance

- `SCRCPY` — device metadata
- `AsyncProcess` — process lifecycle
- `iSCRCPYEmitter` — emitter protocol

## Key methods

- `start()` — requires a running loop; creates queues and starts the child only after the loop check succeeds
- `stop()` / `stopAsync()` — set Event, wait for process exit, then cancel parent receiver and close queues
- `work()` — child-process entry point (override in subclasses)

## Shutdown

1. Shared `Event` is set.
2. Process is joined (or killed if forced).
3. Parent receiver is cancelled (hard cancel) and awaited.
4. Both receivers drain remaining messages (drain is in `finally`, so hard cancel still drains).
5. Queues are closed (`close` + `cancel_join_thread`).

## Notes

- Queue attributes (`_inQueue`, `_outQueue`) use the same names on both sides; they do not collide because each process has its own instance after pickling.
- `isRunning` reports only process liveness.
- Base `_receiver` currently prints messages; subclasses replace the handling logic.
- `start()` raises if called without a running event loop; no process is started in that case.
