## Overview & Design Context

`ServerEndpoint` is the multi-client server transport. It owns the shared inbound queue and three `ClientMap` registries keyed by `clientId`. Clients are introduced exclusively through `spawnClient` and become eligible for traffic only after a successful handshake.

* **Design Decision / Deviation Notes:** See `requirement.md` (ClientMap proxy, three-map lifecycle). Bridge attachment, overload, drain and stop are out of scope for this document.

---

## Classes

### `Proxy[T]`
- **Purpose:** Minimal identity + entity holder.
- **Properties:**
  - `Id` (UUID, readonly) – stable identity.
  - `Entity` (T) – the held object (for maps, a `Queue`).

### `ClientMap` (extends `Proxy[Queue]`)
- **Purpose:** Per-client state proxy used as the value type of all three maps.
- **Properties:**
  - `Id` – the `clientId`.
  - `Entity` – server-outbound / client-inbound `Queue`.
  - `timeout` (int, nanoseconds) – handshake / pending deadline. Setter accepts `float` seconds and converts to nanoseconds.

### `ServerEndpoint`
- **Purpose:** Fan-in / fan-out transport for N clients; owns shared inbound and the three maps.
- **Methods:**
  - `spawnClient(spawner, timeout=2.0) -> UUID` – create Queue + ClientMap, insert into pending, invoke spawner, return clientId.
  - Handshake handler (internal) – applies map transition rules and replies `HSSuccess` / `HSFail`.

---

## Maps

All maps: `Dict[UUID, ClientMap]` keyed by `clientId`.

| Map | Role |
|-----|------|
| `pendingClientMap` | Spawned, awaiting handshake |
| `activeClientMap` | Handshaked / re-activated, eligible for traffic |
| `dormantClientMap` | Soft-deactivated, may be re-activated by a later handshake |

---

## Rules

### R-1 Map key
Every map entry is keyed solely by `clientId` (UUID). No other identifier is used for lookup or transition at this layer.

### R-2 ClientMap completeness
A `ClientMap` always carries a non-None `Entity` (Queue) while it resides in any of the three maps.

### R-3 Timeout representation
`ClientMap.timeout` is stored as nanoseconds. Any API that accepts a timeout in seconds (including `spawnClient` and the Handshake message) converts to nanoseconds on write.

### R-4 Exclusive ownership of shared inbound
Only `ServerEndpoint` owns and reads the shared inbound Queue. Clients never read it.

### R-5 Spawn produces pending only
`spawnClient` must insert into `pendingClientMap` and must not place a new client directly into active or dormant.

---

## Protocols

### P-1 spawnClient
1. Allocate `Queue` (client inbound = server outbound).
2. `clientId = uuid4()`.
3. Build `ClientMap(Id=clientId, Entity=queue, timeout=timeout)`.
4. `pendingClientMap[clientId] = clientMap`.
5. Call `spawner(client_inbound, shared_inbound, clientId, timeout)`.
6. Return `clientId`.

### P-2 Handshake handling
On receipt of `Handshake` carrying `clientId` (and optional `timeout`):

1. If `clientId` in `pendingClientMap`:
   - Move `ClientMap` to `activeClientMap`.
   - Reply `HSSuccess(clientId)`.
2. Else if `clientId` in `dormantClientMap`:
   - Move `ClientMap` to `activeClientMap` (re-activate).
   - Reply `HSSuccess(clientId)`.
3. Else if `clientId` in `activeClientMap`:
   - Leave maps unchanged (idempotent).
   - Reply `HSSuccess(clientId)`.
4. Else:
   - Log a warning.
   - Reply `HSFail(clientId)`.

### P-3 Handshake messages
- `Handshake(Message)` – fields/payload include `clientId` and `timeout`.
- `HSSuccess(Message)` – carries `clientId`.
- `HSFail(Message)` – carries `clientId`.

All three descend from `Message`.

---

## Policy

### Pol-1 Default timeout
`spawnClient` default `timeout` is 2.0 seconds. The value is stored on the `ClientMap` and is also passed to the spawner so the client side can observe the same deadline.

### Pol-2 Re-activation
A client present only in `dormantClientMap` is returned to `activeClientMap` on a matching `Handshake`. No new Queue is allocated.

### Pol-3 Unknown client
A `Handshake` whose `clientId` appears in none of the three maps produces `HSFail` and a warning log. No map entry is created.

### Pol-4 Idempotent active handshake
A `Handshake` for a `clientId` already in `activeClientMap` is treated as success without further map mutation.

---

## Sample Usage

```python
from jAGFx.IPC.endpoint import ServerEndpoint

server = ServerEndpoint()   # owns shared inbound

def my_spawner(client_in, shared_in, client_id, timeout):
    # start worker process/task with the four values
    ...

client_id = server.spawnClient(my_spawner, timeout=2.0)
```
