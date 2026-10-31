# Implementation Details

## 1. Architecture Overview

```text
                    ServerEndpoint
                    ┌─────────────────────────────┐
  clients put ──►   │ shared_inbound: Queue       │
                    │                             │
                    │ pendingClientMap            │
                    │ activeClientMap             │
                    │ dormantClientMap            │
                    │   Dict[UUID, ClientMap]     │
                    │                             │
                    │ ClientMap                   │
                    │   Id, Entity(Queue), timeout│
                    └─────────────────────────────┘
                              │
              spawnClient ────┘
                              │
                              ▼
                         spawner(...)
                              │
                              ▼
                       ClientEndpoint
                       (per worker)
```

- `ServerEndpoint` owns the shared inbound Queue and the three maps.
- `ClientMap` is the value type of every map entry.
- `ClientEndpoint` is constructed only with values produced by `spawnClient`.
- Handshake is the sole transition mechanism among the three maps at this layer.

## 2. Directory & Module Mapping

| Source Path (planned) | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/__serverEndpoint.py` (or equivalent) | `.docs/jAGFx/IPC/endpoint/ServerEndpoint.md` | Multi-client server transport, maps, spawnClient, handshake handler |
| `src/jAGFx/IPC/__clientEndpoint.py` (or equivalent) | `.docs/jAGFx/IPC/endpoint/ClientEndpoint.md` | Client-side endpoint, Handshake emission |
| Proxy / ClientMap (IPC or collections) | covered in ServerEndpoint.md | Minimal state proxy |
| Handshake / HSSuccess / HSFail messages | control or endpoint messages | Handshake protocol messages |

## 3. Core Workflows & Data Flow

### 3.1 Spawn
1. Host calls `server.spawnClient(spawner, timeout=2.0)`.
2. Server allocates Queue + ClientMap, inserts into `pendingClientMap`.
3. Spawner is invoked with `(client_inbound, shared_inbound, clientId, timeout)`.
4. Host/spawner starts the worker; worker builds `ClientEndpoint`.

### 3.2 Handshake
1. `ClientEndpoint` sends `Handshake(clientId, timeout)`.
2. Server applies P-2 transition rules (pending → active, dormant → active, active idempotent, else fail).
3. Server replies `HSSuccess` or `HSFail`.
4. Only after `HSSuccess` is the client considered bound for normal traffic.

### 3.3 Map transitions (summary)

```text
spawnClient          → pendingClientMap
Handshake (pending)  → activeClientMap
Handshake (dormant)  → activeClientMap   (re-activate)
Handshake (active)   → no change         (idempotent)
Handshake (unknown)  → HSFail + warning
(future de-activate) → dormantClientMap
```

## 4. Deferred

- Bridge registration and message routing onto active clients
- Overload policy
- Drain and stop semantics across the three maps
- Server-side enforcement of pending timeout (ClientMap.timeout)
- Concrete module file names under `src/jAGFx/IPC/`
