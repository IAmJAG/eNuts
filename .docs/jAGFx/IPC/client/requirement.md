# Client — Requirements

## Creation (MUST)

- A `Client` or any subclass instance MUST be created only inside `ProcessHost.start`.
- Any other construction raises `RuntimeError("Client and all subclasses MUST be created inside ProcessHost.start.")`.
- The constraint is enforced by the metaclass `_ClientMeta.__call__`. No subclass can bypass it by omitting `super().__init__`.
- Class definition (subclassing) is unrestricted.

## Guard

The static method `_isCalledFromAllowedFactory` returns true only when:

1. The immediate caller of the constructor (via the metaclass) is a function named `start`, and
2. That function’s `self` is an instance of `iProcessHost`.

## State and messaging

- Heartbeat refreshes expiry; missed beat → `DORMANT`.
- Inbound messages are queued and processed only while `ACTIVE`.
- `Terminated` moves the client to `TERMINATED`.
