# Implementation — outOfProcessEmitter

Matches `.docs/fluxCore/emitters/outOfProcessEmitter.md`.

## Phase 0 — worker

`_clientWorker` lives in `src/fluxCore/emitters/__clientWorker.py`. It does not import the emitter. Spawn imports it by name. The emitter imports the worker. It closes only its dedicated inbound. The parent closes the shared inbound.

## Phase 1 — queues

- `_outQueues[clientId]` is the parent's dedicated outbound, the client's inbound.
- `_inQueue` is the parent's single inbound, every client's outbound.
- First `start` creates the inbound queue and the shutdown event.
- A failed start releases only what it created.

## Phase 2 — receiver

One `_receiverTask` on `_inQueue`, started with the first client.

## Phase 3 — liveness

- `running()` is true only when the event exists, is not set, and a process remains.
- `running(clientId)` is true only when that process is alive.

## Phase 4 — shutdown

`ON_STOPPING`, set the event, finish the receiver, join, close queues, `ON_STOPPED`. `stop` coalesces. Failures are reported.

## Phase 5 — acceptance

One script: `.test/smoke/emitters/test_opemitter_message_path.py`.

It runs every check in one pass and records the message path:

```text
parent put(clientId) -> out[clientId] -> client inbound
client echo          -> shared inbound -> parent receiver
```

### `trace`

`trace` is the logging builtin. It is not a print and not a comment.

- Installed by `src/__monkeyPatch.py`: `setattr(builtins, "trace", trace)` from `jAGFx.logging`.
- Declared in `typings/__builtins__.pyi`: `def trace(message, *args, **kwargs) -> None`.
- Level is `TRACE` (5). `setupLogging` defaults to that level, so `trace` is emitted.

The script imports `__monkeyPatch` before any check, then calls `setupLogging`. Every check and every hop calls `trace`:

```text
PASS  roundtrip a:ping
FAIL  addressed: only a replies  [...]
FLOW  parent put(a, ping) -> out[a]
FLOW  parent inbound got 'a:ping'  n=1
```

The echo worker imports `__monkeyPatch` in the child and calls `trace` when it receives and when it echoes. The parent probe calls `trace` when the shared inbound delivers a message.
