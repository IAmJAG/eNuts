# Requirements & Design Specifications

## 1. Project Overview
`FrameBuffer` is a new post-decode cache that supports multiple concurrent consumers via bitwise IDs, a single `next` access point, and automatic timeout-based release. It replaces the need to extend the existing `FrameRing` for this use case.

## 2. Functional Requirements
- **FR-1:** `next(consumerId, sequence=None, timeout=None)` is the only consumer access point and returns an already-acquired `BufferSlot`.
- **FR-2:** When `sequence` is supplied, the returned slot is the adjacent greater sequence; when `None`, the latest sequence is returned.
- **FR-3:** Consumer IDs are unique bit values and may coexist on the same slot.
- **FR-4:** `BufferSlot.release(consumerId=None)` removes one consumer or all consumers.
- **FR-5:** Each slot owns a single timeout; the timeout value comes from the call or from `RingSlotConfiguration.defaultReleaseTimeout`.
- **FR-6:** Buffer size starts at the constructor value and may grow by doubling up to the configured maximum.
- **FR-7:** When no free slot exists and growth is blocked (size or VRAM cap), the oldest slot is evicted regardless of locked/free state; the incoming frame is written into the freed slot.
- **FR-8:** A slot has only two states: locked (consumers present) or free.

## 3. Non-Functional Requirements
- **NFR-1:** Zero-copy: the payload tensor is never cloned by the buffer.
- **NFR-2:** Timeout watcher is an asyncio Task owned by the slot; acquire must occur while a loop is running.
- **NFR-3:** Configuration is resolved via the nested `RingSlotConfiguration` section.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Eviction of locked slots
- **Affected Modules:** `FrameBuffer`, `BufferSlot`
- **Description of Standard / Best Practice:** Normally a leased slot is protected from reuse.
- **Divergence:** Oldest slot is invalidated even if consumers still hold it.
- **Design Decision & Justification:** Guarantees forward progress under memory pressure; consumers must tolerate possible invalidation.
- **Code Doc Cross-Reference:** See `frameBuffer.md` and `implementation.md`.
