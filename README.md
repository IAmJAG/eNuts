# eNuts FrameRing pipeline patch

Target branch: `development`  
Repository: `IAmJAG/eNuts`  
Base checkpoint verified before preparing this patch: `4710b18991e43f6433df5aa4e436e8adeb8badf0`

## Contents

This overlay contains the updated Python source files and the corresponding FrameRing/Presenter documentation. Copy the directory structure over the repository root and review the diff before committing.

## Important API changes

1. `FrameRing.publish()` is now async: callers must `await ring.publish(packet, decoder)`.
2. `latest()` and `next()` now return a leased `RingSlot`, not a tensor clone. Read `slot.payload` and always call `ring.release(slot)` in a `finally` block.
3. The ring owns one bounded decode queue and one serial worker. Queue saturation applies backpressure instead of dropping arbitrary predictive packets.
4. `LocalDeviceStream` starts/stops the worker as part of stream lifecycle.
5. `KGRecorderService` is intentionally unchanged; it records raw encoded packets directly from the emitter.

## Files

- `src/fluxCore/stream/frameRing/__frameRing.py`
- `src/fluxCore/stream/frameRing/slot/__ringSlot.py`
- `src/fluxCore/stream/__presenter.py`
- `src/fluxCore/stream/__deviceStream.py`
- `src/fluxCore/types/interface/stream/frameRing/__frameRing.py`
- `src/fluxCore/types/interface/stream/frameRing/slot/__ringSlot.py`
- `.docs/fluxCore/stream/frameRing/implementation.md`
- `.docs/fluxCore/stream/frameRing/requirement.md`
- `.docs/fluxCore/stream/frameRing/frameRing.md`
- `.docs/fluxCore/stream/presenter/implementation.md`

## Validation status

The patch is syntax-checked locally. Full runtime/integration tests require the project's Python environment, PyAV, CUDA/Torch configuration, and Qt/jAGFx dependencies; run the repository's test suite before committing.
