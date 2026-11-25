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

Parent margin is 0.5 s. Handshake ACK calls `beat(5.0)` to give a longer initial grace; subsequent Heartbeats use the reported window (normally 2.0).

The done-callback `_expire` ignores the callback when:

- the task was cancelled, or
- the task is no longer the current `_expiryTask`, or
- `monotonic_ns() < self._expiry` (a newer beat — including the Handshake ACK — has already extended the deadline).

## Message processor restart

The `clientState` setter starts `_messageProc` when the state becomes `ACTIVE` and the previous task is done. A done-callback on that task restarts the processor if the state is still `ACTIVE` when the task exits. This prevents a transient `DORMANT` (ENDSIGNAL injected) from permanently silencing later Heartbeats.

## Unchanged

`processMessage` behavior.
