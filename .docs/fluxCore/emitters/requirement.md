# outOfProcessEmitter — Requirements

Out-of-process emitter base. Heavy work runs in one or more child processes. The parent stays responsive.

The full contract is `outOfProcessEmitter.md`.

## Work — rule and policy

Work is the heavy method. It is the only code that runs inside a client process.

- Work is a module-level coroutine. Not a bound method. Not a nested function.
- Spawn must import it by name. A bound method would pickle the emitter.
- It receives the shutdown event, that client's inbound queue, and the shared outbound queue. It does not receive the parent.
- It exits when the event is set. It does not own process lifetime.
- One function for every client. Per-client state is the queues it is given.
- Base work observes a message. A subclass replaces the observation, not the transport.
- On exit it releases its own queue handles. The parent still owns and closes the queues it created.

## Functional

- Run that work in one or more child processes.
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
