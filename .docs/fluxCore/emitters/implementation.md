# Implementation — outOfProcessEmitter

Matches `.docs/fluxCore/emitters/outOfProcessEmitter.md`.

## Phase 0 — worker

`_clientWorker` lives in `src/fluxCore/emitters/__clientWorker.py`. It does not import the emitter. Spawn imports it by name. The emitter imports the worker.

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

`.test/smoke/emitters/test_opemitter_message_path.py`
