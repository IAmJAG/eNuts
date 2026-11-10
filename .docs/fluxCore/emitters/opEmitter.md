# OPEmitter

Out-of-process base emitter. Heavy work runs in a separate process while the parent (usually the UI loop) remains responsive.

## Purpose

Separate a heavy method/function into a different process than the main process. Provides bidirectional Queue IPC and a cooperative shutdown protocol.

## Inheritance

- `SCRCPY` — device metadata
- `AsyncProcess` — process lifecycle
- `iSCRCPYEmitter` — emitter protocol

## Key methods

- `start()` — creates queues, starts child process, schedules parent receiver
- `stop()` — sets Event, injects sentinels, joins process, closes queues
- `work()` — child-process entry point (override in subclasses)

## Shutdown protocol

1. Shared `Event` is set.
2. `_SHUTDOWN_SENTINEL` is placed in both directions.
3. Both receivers drain and exit.
4. Queues are closed (`close` + `cancel_join_thread`).
5. Process is joined (or killed if forced).

## Notes

- `isRunning` reports only process liveness (parent tasks are independent).
- Base `_receiver` currently prints messages; subclasses replace the handling logic.
- Requires a running event loop on the parent side when `start()` is called.
