# Implementation Details — Stream pipeline (GPU → GLImage)

## 1. Architecture Overview

```text
Worker: SCRCPYEmitter + ScrcpyRealBridge + frame producer (GPU ring)
Main:   ScrcpyProxyBridge + stream consumer + GLImage (shader fit)
Link:   IPC control/session + GPU interop handles
Meta:   FrameSlotHeader (seq, pts, w, h, stride, format, flags)
```

## 2. Directory & Module Mapping

| Source | Documentation | Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/emitters/scrcpy/__frameSlot.py` | `frameSlot.md` | Slot header + ring helpers (**P1 done**) |
| `src/jAGFx/IPC/*` | `.docs/jAGFx/IPC/IPC.md` | Control Endpoint/Bridge |
| `src/fluxCore/emitters/scrcpy/__bridge.py` | scrcpy `bridge.md` | Control bridges |
| `src/jAGQt/widgets/Image/__glImage.py` | glImage.md | Present + shader fit (**P2**) |
| `src/eNuts/application/recorder/__kgRecorder.py` | — | Attach stream (**P6**) |

## 3. Phase status

| Phase | Status |
|-------|--------|
| P0 | **Done** |
| P1 | **Done** |
| P2–P7 | Pending |
