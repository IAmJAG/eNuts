# Requirements & Design Specifications

## 1. Project Overview

IPC provides a bidirectional, process-local message channel between two processes. Domain entities attach through a generalized Bridge. The transport is entity-agnostic. All cross-process message traffic is asynchronous.

## 2. Functional Requirements

- **FR-1:** `IOQueue.createPair()` returns a pair of `multiprocessing.Queue` objects only. Each process constructs its own `IOQueue` adapter.
- **FR-2:** `IOQueue` encodes outbound messages to JSON and decodes inbound JSON via the project serializer.
- **FR-3:** `Message` carries payload, `messageId`, `correlationId`, chronologically sortable `timestamp` (epoch float), and `isTerminal`.
- **FR-4:** One `Endpoint` type (`jAGFx.IPC.Endpoint`) is used on both ends. It owns inbound/outbound tasks, kind dispatch, and `correlationId → bridge`.
- **FR-5:** Bridges register with the endpoint, expose message handlers, and push outbound traffic via `await endpoint.send(message)` (or `bridge.send`).
- **FR-6:** Request is a subtype of command. There is no IPC Future/blocking reply API.
- **FR-7:** Correlation is two-level: endpoint maps `correlationId → bridge`; bridge maps `correlationId → processor`.
- **FR-8:** On terminal send: if mapped, endpoint drops correlation and bridge processor, then the message is still pushed. Register correlation only when not terminal.
- **FR-9:** Process entry points under Windows `spawn` are module-level callables. Only queue objects and plain config cross the boundary.

## 3. Non-Functional Requirements

- **NFR-1:** Receive polling uses a finite timeout so shutdown can be observed.
- **NFR-2:** Large binary payloads do not rely on JSON through the message queue (future path).
- **NFR-3:** Queue handle ownership and close behavior remain explicit at process lifecycle boundaries.
- **NFR-4:** All IPC send/dispatch paths involving messages are async.

## 4. Design Decisions

### Symmetric Endpoint
Both processes use the same `Endpoint` class; only queue orientation differs.

### Terminal flag
Any message kind may set `isTerminal`. Unmap-if-present, then still deliver/push.

### Request ⊂ command
No special Future-based request API on the endpoint.

### `createPair` returns queues
Prevents accidentally passing an `IOQueue` across the process boundary.

### Provisional kind resolution
`payload.kind` if a non-empty str, else `type(payload).__name__`. Concrete bridges may refine this later.
