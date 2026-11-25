# Client — Implementation

## Creation guard (MUST)

Enforced by metaclass `_ClientMeta.__call__` so every instantiation of `Client` or any subclass is intercepted before `__init__` runs.

```python
class _ClientMeta(type):
    def __call__(cls, *args, **kwargs):
        if not Client._isCalledFromAllowedFactory():
            raise RuntimeError(
                "Client and all subclasses MUST be created inside ProcessHost.start."
            )
        return super().__call__(*args, **kwargs)

class Client(..., metaclass=_ClientMeta):
    def __init__(self, clientId: int):
        super().__init__()
        # ... remainder unchanged; no guard here ...
```

`_isCalledFromAllowedFactory` walks two frames back (through the metaclass) and checks:

```python
functionName == "start" and isinstance(me, iProcessHost)
```

This matches the call site in `ProcessHost.start`:

```python
client: iClient = clientType(clientId=identity)
```

## Why metaclass

A check only in `__init__` can be skipped by a subclass that does not call `super().__init__`. The metaclass makes the constraint impossible to bypass.

## Heartbeat expiry race resistance

`beat()` records the absolute deadline in `self._expiry` (monotonic_ns) *before* cancelling the previous task or scheduling the new one.

Parent margin is 1.0 s. Handshake ACK calls `beat(5.0)` to give a longer initial grace; subsequent Heartbeats use the reported window (normally 2.0).

The done-callback `_expire` ignores the callback when:

- the task was cancelled, or
- the task is no longer the current `_expiryTask`, or
- `monotonic_ns() < self._expiry` (a newer beat — including the Handshake ACK — has already extended the deadline).

## Recovery from DORMANT

`push` always enqueues `Heartbeat` and `Terminated`, even when the client is not `ACTIVE`.  
The `clientState` setter injects `ENDSIGNAL` only on `TERMINATED`. A `DORMANT` transition leaves the message processor running so the next Heartbeat can be processed, call `beat()`, and return the client to `ACTIVE`.

A done-callback on the processor task restarts it if the task exits while the state is still `ACTIVE`.

## Unchanged

`processMessage` behavior.
