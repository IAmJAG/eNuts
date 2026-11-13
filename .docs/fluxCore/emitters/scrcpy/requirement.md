# Requirements — SCRCPY emitter / bridge

## Done (A–D)

- **FR-A:** `toScrcpy`, `SCRCPYError`, `asyncRaiseEvent`.
- **FR-B:** Message types under `emitters/scrcpy/`.
- **FR-C1–C3:** Real/proxy bridges, correlated initialize, smoke without ADB.
- **FR-D:** Inventory / documentation close-out for this track.

## Done (2026-11-13)

- **FR-Meta-Timeout:** `_updateMetadata` must not block indefinitely. Each header field (device name, codec, width, height) is read under `asyncio.wait_for` (default 5s). Timeout or disconnect raises through `initialize.metadata` so callers (`DeviceManager.ensureRunning`) surface the failure. Success still emits the `metadata id=…` trace and `ON_METADATA_UPDATE`.

## Deferred (separate tracks)

Frame transport, shared memory, process host, UI integration, control injection.
