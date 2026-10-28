# Requirements & Design Specifications

## 1. Project Overview

Bidirectional process-local message channel. Bridges attach domain entities.
All cross-process traffic is asynchronous.

## 2. Functional Requirements

- **FR-1:** `IOQueue.createPair()` returns queue objects only; each process builds its own adapter.
- **FR-2:** Messages carry payload, ids, optional `ownerId`, timestamp, `isTerminal`.
- **FR-3:** Endpoint routes by `ownerId` / default Bridge ID only.
- **FR-4:** Bridge owns correlation trackers, processors, terminal policy, MRO type dispatch.
- **FR-5:** Endpoint exposes `OverloadPolicy` + optional outbound capacity; default UNBOUNDED.
- **FR-6:** `stop(drainTimeout)` drains outbound then closes the IOQueue.
- **FR-7:** Receive/dispatch/outbound errors are observed and back off; not silent forever.
- **FR-8:** Peer alive map `_bridgeAlive[bridgeId]` updated by Hello/Heartbeat; no second ID system.
- **FR-9:** Main→peer sends should require `isBridgeAlive(peerBridgeId)` (application gate).

## 3. Non-Functional Requirements

- **NFR-1:** Finite receive timeout for shutdown observability.
- **NFR-2:** Error backoff capped; CancelledError still stops loops.
- **NFR-3:** Handler errors do not auto-terminal correlations.

## 4. Design Decisions

### Default Bridge as UUID
Single source of truth in `_bridges`.

### Peer alive vs local registry
`_bridges` = local instances. `_bridgeAlive` = peer bridgeIds heard via control messages.

### Overload as option
Recording paths keep UNBOUNDED; other paths may set capacity + policy.
