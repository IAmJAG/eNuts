# Stream Pipeline — Implementation Plan

**Status:** P0–P1 done; P2–P5 partial; **stopped — discuss GPU interop**  
**Branch:** `development`

## Phase status

| Phase | Status | Notes |
|-------|--------|-------|
| P0 | **Done** | |
| P1 | **Done** | `__frameSlot.py` |
| P2 | **Partial** | `GLImage.presentExternal`; resize refit; still CPU scale transitional |
| P3 | **Partial** | `FrameRing` (headers + opaque payload) |
| P4 | **Blocked** | Worker needs exportable GPU handles |
| P5 | **Partial** | `LocalDeviceStream` in-process; `IpcDeviceStream` → NotImplementedError |
| P6 | **Blocked** | Needs IPC path + view vs input surface decision |
| P7 | Pending | |

## STOP — conflicts for discussion

1. **Cross-process GPU interop (plane E)** cannot be finished in pure Python/Qt (DMABUF / EGLImage / IOSurface / D3D shared handles need platform native code). Without it, multi-process zero-copy present is incomplete.
2. **Shader fit** is not yet true GLSL sampling — transitional path still CPU-scales into a draw QImage.
3. **KGRecorder** expects CaptureImage input signals; **PlaybackBase** already uses **GLImage** `_streamView` (display only).

## Landed code

| Path | Role |
|------|------|
| `src/jAGQt/widgets/Image/__glImage.py` | `presentExternal` / `clearPresent` |
| `src/fluxCore/emitters/scrcpy/__frameRing.py` | Ring publish / latest / display |
| `src/eNuts/application/stream/` | `LocalDeviceStream`, stub `IpcDeviceStream` |
| `.test/smoke/scrcpy/test_frame_ring.py` | Ring smoke |

## Resume options

A. Add platform GPU importer/exporter (true E)  
B. Temporary IPC frame plane via SHM RGB (design C fallback) to unblock P4–P6  
C. Wire **local-only** P6 (`LocalDeviceStream` → `_streamView`) now; defer multi-process  
