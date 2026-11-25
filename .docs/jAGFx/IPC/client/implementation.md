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

## Unchanged

Heartbeat timing, message queue, state setter, and `processMessage` behavior.
