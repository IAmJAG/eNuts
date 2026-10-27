# Requirements & Design Specifications

## 1. Project Overview

IPC provides a bidirectional, process-local message channel between two processes. Domain entities that must live in one process while being controlled or observed from another are attached through a generalized Bridge. The transport itself is entity-agnostic.

## 2. Functional Requirements

- **FR-1:** `IOQueue.createPair()` returns a pair of `multiprocessing.Queue` objects only. Each process constructs its own `IOQueue` adapter.
- **FR-2:** `IOQueue` encodes outbound `iMessage` instances to JSON and decodes inbound JSON via the project serializer.
- **FR-3:** `Message` carries a serializable payload, a unique `messageId`, and an optional `correlationId` so either side can originate request/response pairs.
- **FR-4:** A single `CommunicationManager` type is used on both ends. It owns inbound polling, outbound sending, correlation, and handler registration.
- **FR-5:** Command handlers may be registered on either side. Either side may send commands, responses, or events.
- **FR-6:** A Bridge binds a domain entity to the local manager. On the owner process it drives the real entity; on the peer process it presents a proxy surface. The same conceptual component covers both roles.
- **FR-7:** Process entry points used under Windows `spawn` must be module-level callables. Only queue objects (and plain config) cross the boundary.

## 3. Non-Functional Requirements

- **NFR-1:** Receive polling uses a finite timeout so shutdown can be observed without permanently blocking a worker thread.
- **NFR-2:** Large binary payloads (e.g. video frames) must not rely on JSON through the message queue; a separate descriptor + shared-memory (or equivalent) path is required when needed.
- **NFR-3:** Queue handle ownership and close/join behavior must be explicit so one side does not close a queue the other still uses.

## 4. Design Decisions & Standards Deviations

### Item 1: Symmetric managers instead of main/client specialization
- **Affected Modules:** `src/jAGFx/IPC/`, proposed CommunicationManager / Bridge
- **Description of Standard / Best Practice:** Many IPC designs designate a “server” or “main” side that owns correlation and a “client” that only answers.
- **Divergence:** Both ends run the same manager, both maintain correlation maps, both register handlers.
- **Design Decision & Justification:** Either process may originate work. Treating the sides as identical except for queue orientation keeps the model small and avoids special-case APIs.
- **Code Doc Cross-Reference:** `.docs/jAGFx/IPC/IPC.md` sections 1, 3.4, 4, 7.

### Item 2: `createPair` returns queues, not adapters
- **Affected Modules:** `src/jAGFx/IPC/__IOQueue.py`, `src/jAGFx/types/interface/communication/__IOQueue.py`
- **Description of Standard / Best Practice:** Factory methods sometimes return ready-to-use endpoint objects.
- **Divergence:** `createPair` returns only the two queues; callers build adapters locally.
- **Design Decision & Justification:** `IOQueue` instances must never cross the process boundary under Windows spawn. Returning queues makes the ownership rule impossible to violate by accident.
- **Code Doc Cross-Reference:** `.docs/jAGFx/IPC/IPC.md` section 2; implementation in `__IOQueue.py`.

### Item 3: Generalized Bridge (not entity-specific)
- **Affected Modules:** proposed Bridge layer
- **Description of Standard / Best Practice:** Some systems hard-wire IPC to a single remote object type.
- **Divergence:** Bridge is a reusable pattern for any entity with commands and events; concrete entities (including SCRCPY-related ones) are examples, not the architecture center.
- **Design Decision & Justification:** Multiple remote resources will need the same pattern. Keeping the transport and manager entity-agnostic avoids repeated redesign.
- **Code Doc Cross-Reference:** `.docs/jAGFx/IPC/IPC.md` sections 1, 3.5, 8, 13.
