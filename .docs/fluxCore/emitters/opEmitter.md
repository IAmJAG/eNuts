# OPEmitter

Out-of-process base emitter. Heavy work runs in a separate process while the parent (usually the UI loop) remains responsive.

## Purpose

Separate a heavy method/function into a different process than the main process. Provides bidirectional Queue IPC and a cooperative shutdown via a shared Event.

## Inheritance

- `AsyncProcess` — process lifecycle
- `SCRCPY` — device metadata

Satisfies `iSCRCPYEmitter` structurally. It is **not** an explicit base. The three protocol orders cannot be linearized:

- `SCRCPY` contributes `iDevice` early
- `AsyncProcess` contributes `iSubscription` before `iService`
- `iEmitter` wants `iService`, `iSubscription`, `iDevice`

Same pattern as `SCRCPYEmitter`.

## Key methods

- `start()` — requires a running loop; creates queues and starts the child only after the loop check succeeds
- `stop()` / `stopAsync()` — AsyncProcess owns process exit and events; OPEmitter then cancels the parent receiver and closes queues
- `work()` — child-process entry point (override in subclasses)

## Shutdown

1. `AsyncProcess.stop*` sets the Event, joins or kills, closes the handle, raises `ON_STOPPING` / `ON_STOPPED`.
2. Parent receiver is cancelled (hard cancel) and awaited. Drain runs in `_receiver` `finally`.
3. Queues are closed (`close` + `cancel_join_thread`).

## Notes

- Queue attributes (`_inQueue`, `_outQueue`) use the same names on both sides; they do not collide because each process has its own instance after pickling.
- `isRunning` reports only process liveness.
- Base `_receiver` currently prints messages; subclasses replace the handling logic.
- `start()` raises if called without a running event loop; no process is started in that case.
