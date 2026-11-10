# OPEmitter

Out-of-process base emitter. Heavy work runs in a separate process while the parent (usually the UI loop) remains responsive.

## Purpose

Separate a heavy method/function into a different process than the main process. Provides bidirectional Queue IPC and a cooperative shutdown via a shared Event.

## Inheritance

- `SCRCPY` — device metadata
- `AsyncProcess` — process lifecycle
- `iSCRCPYEmitter` — emitter protocol

## Key methods

- `start()` — creates queues, starts child process, schedules parent receiver
- `stop()` — sets Event, joins process, cancels parent receiver, closes queues
- `work()` — child-process entry point (override in subclasses)

## Shutdown

1. Shared `Event` is set.
2. Both receivers exit their loops and drain remaining messages.
3. Queues are closed (`close` + `cancel_join_thread`).
4. Process is joined (or killed if forced).

## Notes

- Queue attributes (`_inQueue`, `_outQueue`) use the same names on both sides; they do not collide because each process has its own instance after pickling.
- `isRunning` reports only process liveness.
- Base `_receiver` currently prints messages; subclasses replace the handling logic.
- Requires a running event loop on the parent side when `start()` is called.
