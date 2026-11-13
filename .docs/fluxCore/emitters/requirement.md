# outOfProcessEmitter — Requirements

Out-of-process emitter base. Heavy work runs in one or more child processes. The parent stays responsive.

The full contract is `outOfProcessEmitter.md`.

## `_clientWorker` — rule and policy

`_clientWorker` is the child entry. It is the only code that runs inside a client process.

- It is a module-level coroutine.
- It lives in its own module, not in the `outOfProcessEmitter` module.
- It is not a method, not nested, and not a bound method.
- Spawn imports it by name from that module. The child loads the worker module, not the emitter class.
- It receives the shutdown event, that client's inbound queue, and the shared outbound queue. It does not receive the emitter.
- It exits when the event is set. It does not own process lifetime.
- One function for every client. Per-client state is the queues it is given.
- The emitter imports the worker. The worker does not import the emitter.

### Why module level

Windows starts children with `spawn`, not `fork`. The child is a new interpreter and rebuilds the target by importing it.

- A nested function has no import path. Spawn fails with `Can't get local object`.
- A bound method pickles the emitter, including its other process handles and queues. That is forbidden.
- A module-level function has a stable import path. Spawn imports that and calls it.

### Why its own module

The emitter module imports the device, the process base, and the parent class. The child does not need any of that. A separate worker module means the child imports only the worker.

## Functional

- Run `_clientWorker` in one or more child processes.
- Parent → client: one dedicated outbound queue per client.
- Client → parent: one shared inbound queue, one parent receiver.
- Cooperative shutdown via one shared event. Forced stop is explicit.
- `running()` and `running(clientId)` as specified in the contract.

## Non-functional

- Must not block the parent event loop.
- Must not leave a process, a queue, or a feeder thread after stop.
- Must tolerate forced termination.
- Must be usable as a base class.

## Constraints

- Bases are `AsyncProcess` and `SCRCPY`.
- Satisfies `iSCRCPYEmitter` structurally. It is not an explicit base.
- Parent owns every queue.
