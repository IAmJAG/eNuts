# Stream Pipeline — Implementation Plan

**Platform:** Windows only  
**Chosen stack (most likely to work):** software decode + in-process present  
**Branch:** `development`

## Locked stack

```text
SCRCPYEmitter.initialize(GPUReady=False)   # PyAV SW codec
  → ON_FRAME packets
LocalDeviceStream                          # decode → QImage
  → FrameRing (seq/pts headers)
  → GLImage.presentExternal(...)
KGRecorder binds page._streamView (GLImage)
```

- **Not** CUDA/NVDEC/D3D zero-copy for v1 (deferred; high risk).
- **Not** CaptureImage for stream (removed from KGRecorder bind path).
- Control inject remains best-effort against GLImage geometry; view-first.

## Phase status

| Phase | Status |
|-------|--------|
| P0–P1 | Done (slot contract) |
| P2 | Partial (`presentExternal` on GLImage) |
| P3 | Partial (`FrameRing`) |
| P5 local | **Done** (`LocalDeviceStream`) |
| P6 local | **Done** (KGRecorder → `_streamView`) |
| P4/IPC frames | Deferred (needs SHM or GPU interop later) |
| True E GPU | Deferred (Windows D3D path, separate project) |

## Code touch points

| Path | Role |
|------|------|
| `src/eNuts/application/recorder/__kgRecorder.py` | GLImage + LocalDeviceStream |
| `src/eNuts/application/stream/__deviceStream.py` | Local present path |
| `src/eNuts/application/device/__deviceManager.py` | `initialize(GPUReady=False)` |
| `src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py` | default `GPUReady=False` |
| `src/jAGQt/widgets/Image/__glImage.py` | `presentExternal` |
