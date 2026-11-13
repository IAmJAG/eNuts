# Implementation — outOfProcessEmitter

As built. Contract is `outOfProcessEmitter.md`.

## Files

| File | Role |
|------|------|
| `src/fluxCore/emitters/__outProcessEmitter.py` | Parent. Owns queues, processes, the receiver, shutdown. |
| `src/fluxCore/emitters/__clientWorker.py` | `_clientWorker`. Child entry. Does not import the emitter. |
| `src/fluxCore/emitters/__helper.py` | `closeQueue`, `asyncCloseQueue`. Close plus cancel the feeder thread. |
| `.test/smoke/emitters/test_opemitter_message_path.py` | One acceptance script. |

## Worker

`_clientWorker` is a module-level coroutine in its own module. Spawn imports it by name through `processEntry`. The emitter imports the worker. The worker does not import the emitter.

Signature: `(clientId, shutdownEvent, inQueue, outQueue)`.

- `inQueue` is the parent's dedicated outbound to this client. The worker closes this handle on exit.
- `outQueue` is the parent's shared inbound. The worker does not close it. One client must not cut off the others.
- It exits when the event is set. Timed `get` (0.1 s) so the event is observed without a blocked thread.
- Base behavior prints the message. A caller supplies a different module-level worker via `worker=` on the constructor. Not a method override.

## Queues

| Attribute | Owner view | Client view | Cardinality |
|-----------|------------|-------------|-------------|
| `_outQueues[clientId]` | outbound to that client | its inbound | one per client |
| `_inQueue` | the inbound | its outbound | one for all clients |

First `start` creates `_inQueue` and the shutdown event. Each `start` creates that client's outbound queue and a daemon process named `PROC_{clientId}`.

A failed start closes the client queue, terminates that process, and if no clients remain closes the shared inbound and clears the event.

## Receiver

One `_receiverTask` on `_inQueue`, created with the first client. Polls with a 0.1 s timed get off the loop. Prints. A subclass replaces `_receiver` to record or handle.

## Liveness

- `running()` — event exists, is not set, and process count is greater than zero.
- `running(clientId)` — that process exists and is alive.

## Shutdown

`stop` with a loop schedules one retained `stopAsync` task. A second `stop` while it runs returns. `waitStopped` awaits it. A failure is reported on the loop exception handler.

`stop` with no loop is synchronous and follows the same order.

1. `ON_STOPPING`.
2. Set the event.
3. Finish the receiver (it exits on the event; the no-loop path cancels it).
4. Join each child. `forced` terminates first. Still alive: terminate, then kill.
5. Close every outbound queue and the shared inbound. Cancel feeder threads. Clear state.
6. `ON_STOPPED`.

Cleanup is in `finally`.

## Send

`_dispatch(clientId, msg)` puts on that client's outbound queue, off the loop.

## Acceptance

`.test/smoke/emitters/test_opemitter_message_path.py` runs every check in one pass.

`trace` is the logging builtin. Installed by `src/__monkeyPatch.py` (`setattr(builtins, "trace", trace)` from `jAGFx.logging`). Declared in `typings/__builtins__.pyi`. Level `TRACE` (5). `setupLogging` defaults to that level.

The script imports the patch, calls `setupLogging`, and `trace`s every check and every hop. The echo worker imports the patch in the child and `trace`s receive and echo. The probe `trace`s each parent inbound delivery.

The no-loop check runs before `asyncio.run`. Inside `run` a loop already exists, so that check would pass a start that should fail.
