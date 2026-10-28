# Requirements & Design Specifications

## 1. Project Overview

IPC provides a bidirectional, process-local message channel between two processes.
Domain entities attach through a generalized Bridge. The transport is entity-agnostic.
All cross-process message traffic is asynchronous.

## 2. Functional Requirements

- **FR-1:** `IOQueue.createPair()` returns a pair of `multiprocessing.Queue` objects only. Each process constructs its own `IOQueue` adapter.
- **FR-2:** `IOQueue` encodes outbound messages to JSON and decodes inbound JSON via the project serializer.
- **FR-3:** `Message` carries payload, `messageId`, `correlationId`, optional `ownerId`, chronologically sortable `timestamp`, and `isTerminal`.
- **FR-4:** One `Endpoint` type is used on both ends. It owns inbound/outbound tasks and routes exclusively by `ownerId` / default Bridge ID.
- **FR-5:** Bridges register with the endpoint (`registerBridge(..., asDefault=False)`), expose message handlers, and push outbound traffic via `await bridge.send(message)`.
- **FR-6:** Request is a subtype of command. There is no IPC Future/blocking reply API.
- **FR-7:** Correlation lifecycle is entirely Bridge-owned (AMTT, DMTT, processors, policies).
- **FR-8:** Terminal message policy (Bridge): immediate full removal from all correlation collections.
- **FR-9:** Process entry points under Windows `spawn` are module-level callables. Only queue objects and plain config cross the boundary.
- **FR-10:** `_defaultBridgeId` is a `UUID | None` that indexes into the Endpoint's `_bridges` registry; it is never a live Bridge reference.

## 3. Non-Functional Requirements

- **NFR-1:** Receive polling uses a finite timeout so shutdown can be observed.
- **NFR-2:** Large binary payloads do not rely on JSON through the message queue (future path).
- **NFR-3:** Queue handle ownership and close behavior remain explicit at process lifecycle boundaries.
- **NFR-4:** All IPC send/dispatch paths involving messages are async.
- **NFR-5:** Correlation timeout services use monotonic time and interruptible waits (`AsyncService.wake` / live `throttle`).

## 4. Design Decisions

### Symmetric Endpoint
Both processes use the same `Endpoint` class; only queue orientation differs.

### Owner-based routing
Endpoint selects the Bridge solely by `message.ownerId` (or the configured default). Message type is consulted only inside the selected Bridge.

### Default Bridge as UUID
`_defaultBridgeId` stores the Bridge's ID, not the Bridge object, so the registry remains the single source of truth.

### Terminal policy on Bridge
Immediate full cleanup, same observable effect as the former Endpoint-owned path, but ownership is unambiguous.

### Active / dormant stages
Prevents unbounded growth when a non-terminal conversation is abandoned, while still allowing a grace period for late replies.
