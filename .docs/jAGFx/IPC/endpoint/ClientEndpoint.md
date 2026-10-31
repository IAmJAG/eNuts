## Overview & Design Context

`ClientEndpoint` is the process-local transport used by each worker. It is constructed with the three values supplied by `ServerEndpoint.spawnClient`’s spawner and is responsible for emitting the initial `Handshake`.

* **Design Decision / Deviation Notes:** Client side remains a simple 1:1 adapter over the two queues it receives. All multi-client registry logic lives exclusively on `ServerEndpoint`. See `requirement.md`.

---

## Classes

### `ClientEndpoint`
- **Purpose:** Client-side endpoint. Sends `Handshake` on start; thereafter exchanges ordinary messages over the provided queues.
- **Construction arguments:**
  - `client_inbound` (`Queue`) – messages from server.
  - `shared_inbound` (`Queue`) – messages to server (shared among all clients).
  - `clientId` (`UUID`) – identity minted by `ServerEndpoint.spawnClient`.
- **Methods:**
  - start / stop lifecycle (details deferred with overload/drain).
  - On start: emit `Handshake(clientId, timeout)`.
  - send / receive ordinary messages after successful handshake.

---

## Rules

### R-C1 Construction contract
`ClientEndpoint` must be given exactly the three values delivered by the spawner: client inbound Queue, shared inbound Queue, and `clientId`. It must not invent a new `clientId`.

### R-C2 Handshake obligation
On start, `ClientEndpoint` must send a `Handshake` carrying the supplied `clientId` and the timeout it was given (or the default).

### R-C3 No map ownership
`ClientEndpoint` never touches `pendingClientMap`, `activeClientMap` or `dormantClientMap`. Those exist only on the server.

---

## Protocols

### P-C1 Startup handshake
1. Receive `(client_inbound, shared_inbound, clientId, timeout)` from spawner.
2. Construct `ClientEndpoint`.
3. On start, send `Handshake` with `clientId` and `timeout`.
4. Await `HSSuccess` or `HSFail`.
5. On `HSSuccess` proceed to normal operation; on `HSFail` surface the failure to the host.

### P-C2 Message direction
- Outbound (client → server): put on `shared_inbound`.
- Inbound (server → client): get from `client_inbound`.

---

## Policy

### Pol-C1 Timeout observation
The timeout value received from the spawner is the same value stored on the server-side `ClientMap`. The client may use it as a local deadline for receiving `HSSuccess` / `HSFail`.

### Pol-C2 Failure handling
Receipt of `HSFail` or expiry of the local handshake deadline constitutes a failed bind. The client must not attempt normal traffic until a successful handshake has occurred.

---

## Sample Usage

```python
# Inside the callable passed to ServerEndpoint.spawnClient
def spawner(client_in, shared_in, client_id, timeout):
    endpoint = ClientEndpoint(client_in, shared_in, client_id)
    # start endpoint (async context); it will send Handshake
    ...
```
