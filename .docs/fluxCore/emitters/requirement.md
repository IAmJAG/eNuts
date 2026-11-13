# outOfProcessEmitter — Requirements, Rules, and Mental Model

Out-of-process emitter base. Heavy work runs in one or more child processes. The parent (normally the UI event loop) stays responsive.

This document states the contract. It does not prescribe how to implement it.

The full contract, including the mental model, rules, policies, available technology, and acceptance checks, lives in `outOfProcessEmitter.md` in this directory.

## Functional

- Run heavy work in one or more child processes.
- Parent → client: one dedicated outbound queue per client. That queue is the client's inbound.
- Client → parent: one shared inbound queue on the parent. That queue is every client's outbound.
- One parent receiver on the shared inbound queue.
- Cooperative shutdown via one shared event. Forced stop is explicit.
- `running()` and `running(clientId)` as specified in the contract.

## Non-functional

- Must not block the parent event loop.
- Must not leave a process, a queue, or a feeder thread after stop.
- Must tolerate forced termination.
- Must be usable as a base class.
- Child entry must be spawn-safe.

## Constraints

- Bases are `AsyncProcess` and `SCRCPY`.
- Satisfies `iSCRCPYEmitter` structurally. It is not an explicit base.
- Parent owns every queue.
