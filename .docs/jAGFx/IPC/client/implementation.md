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

The done-callback `_expire` ignores the callback when:

- the task was cancelled, or
- the task is no longer the current `_expiryTask`, or
- `monotonic_ns() < self._expiry` (a newer beat — including the Handshake ACK — has already extended the deadline).

This makes the ACK (and every subsequent Heartbeat) the authoritative key that prevents a stale expiry from marking the client DORMANT.

## Unchanged

Message queue, state setter, and `processMessage` behavior.
