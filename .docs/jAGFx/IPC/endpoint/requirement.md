# Requirements & Design Specifications

## 1. Project Overview

Multi-client inter-process communication for eNuts. One `ServerEndpoint` serves N clients. Each client runs a `ClientEndpoint`. Transport is queue-based; identity and lifecycle are managed by three `ClientMap`-backed maps keyed by `clientId`.

Bridge attachment, overload policy, drain and stop semantics are out of scope for this specification.

## 2. Functional Requirements

- **FR-1:** `ServerEndpoint` owns exactly one shared inbound `Queue`. All clients write to it.
- **FR-2:** `ServerEndpoint` maintains three maps, each `Dict[UUID, ClientMap]` and keyed by `clientId`:
  - `pendingClientMap`
  - `activeClientMap`
  - `dormantClientMap`
- **FR-3:** `ClientMap` is a minimal state proxy (`Proxy[Queue]`) holding the server-outbound / client-inbound `Queue`, a readonly `Id` (`clientId`), and a `timeout` expressed in nanoseconds.
- **FR-4:** `ServerEndpoint.spawnClient(spawner, timeout=2.0)` creates a `Queue` and a `ClientMap`, inserts the map into `pendingClientMap`, then invokes the supplied spawner with `(client_inbound, shared_inbound, clientId, timeout)`.
- **FR-5:** Handshake messages:
  - `Handshake(Message)` carries `clientId` and `timeout`.
  - `HSSuccess(Message)` and `HSFail(Message)` carry `clientId`.
- **FR-6:** On `Handshake` the server applies the map transition rules (see Protocols) and replies with `HSSuccess` or `HSFail`.
- **FR-7:** `ClientEndpoint` is constructed with the three values delivered by the spawner and, on start, emits `Handshake`.
- **FR-8:** Map keys are exclusively `clientId` (UUID). No other identifier is used for map lookup at this layer.

## 3. Non-Functional Requirements

- **NFR-1:** Timeout values accepted by `ClientMap` and `spawnClient` are floats in seconds; stored and compared as nanoseconds.
- **NFR-2:** Default handshake-related timeout is 2.0 seconds.
- **NFR-3:** Map operations must be safe under concurrent handshake and spawn (implementation may serialise or lock).

## 4. Design Decisions & Standards Deviations

### Item 1: ClientMap as Proxy[Queue]
- **Affected Modules:** forthcoming `ServerEndpoint`, map handling
- **Description of Standard / Best Practice:** Direct `Dict[UUID, Queue]` is common for simple registries.
- **Divergence:** A thin proxy (`ClientMap`) carries the Queue plus timeout and identity instead of a bare Queue.
- **Design Decision & Justification:** Keeps related per-client state (timeout, future status flags) co-located without expanding the map value into an ad-hoc tuple or dict. Matches the project preference for explicit, named state holders.
- **Code Doc Cross-Reference:** `ClientMap` / `Proxy` sections in `ServerEndpoint.md` and `implementation.md`.

### Item 2: Three-map lifecycle (pending / active / dormant)
- **Affected Modules:** `ServerEndpoint` handshake handler
- **Description of Standard / Best Practice:** Single connected-client registry with optional soft-delete flags.
- **Divergence:** Explicit pending → active → dormant transitions driven solely by handshake outcomes and (future) de-activation.
- **Design Decision & Justification:** Separates “spawned but not yet confirmed”, “live”, and “soft-idle / re-activatable” so handshake logic stays declarative and re-activation is first-class.
- **Code Doc Cross-Reference:** Rules, Protocols and Policy sections below and in `ServerEndpoint.md`.
