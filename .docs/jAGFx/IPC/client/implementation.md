# Client — Implementation

## Creation guard

Implemented in `Client.__init__` (not `__init_subclass__`).

```python
def __init__(self, clientId: int):
    if not self._isCalledFromAllowedFactory():
        raise RuntimeError("Client can only be created inside ProcessHost.start.")
    super().__init__()
    # ... remainder unchanged ...
```

`_isCalledFromAllowedFactory` walks two frames back from itself and checks:

```python
functionName == "start" and isinstance(me, iProcessHost)
```

This matches the call site in `ProcessHost.start`:

```python
client: iClient = clientType(clientId=identity)
```

## Removed

- `__init_subclass__` that previously raised on every subclass definition.
- Incorrect `isinstance(classType, iProcessHost)` (class object check).

## Unchanged

Heartbeat timing, message queue, state setter, and `processMessage` behavior.
