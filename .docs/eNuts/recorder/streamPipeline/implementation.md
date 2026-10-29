# Implementation Details — Stream pipeline (GPU → GLImage)

## 1. Architecture Overview

```text
Worker: SCRCPYEmitter + ScrcpyRealBridge + frame producer (GPU ring)
Main:   ScrcpyProxyBridge + stream consumer + GLImage (shader fit)
Link:   IPC control/session + GPU interop handles (not pixel queues)
UI:     K&G Recorder hosts GLImage
```

Phases: see `implementationPlan.md` (P0–P7).

## 2. Directory & Module Mapping

| Source (planned / existing) | Documentation | Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/IPC/*` | `.docs/jAGFx/IPC/IPC.md` | Control Endpoint/Bridge |
| `src/fluxCore/emitters/scrcpy/__bridge.py` | `.docs/fluxCore/emitters/scrcpy/bridge.md` | Scrcpy control bridges |
| `src/fluxCore/emitters/scrcpy/` (+ frame slot/producer) | `.docs/eNuts/recorder/streamPipeline/` | Frame plane producer |
| `src/jAGQt/widgets/Image/__glImage.py` | `.docs/jAGQt/widgets/Image/glImage.md` | Present + shader fit |
| `src/eNuts/application/recorder/__kgRecorder.py` | (recorder docs) | Attach stream → GLImage |
| Worker entry (planned under `eNuts/application/ipc/`) | this folder | Client process host |

## 3. Core Workflows

### Stream open

1. Main and worker share Endpoint pair.  
2. `openStream(serial)` agrees format, ring N (2–4), exports GPU handles.  
3. Slot headers carry per-frame geometry; IPC used for session and rare changes.

### Frame publish (client)

1. Decode (prefer HW) → agreed present format.  
2. Write non-display slot + header (`seq`, w, h, …).  
3. Publish ready; optional `FrameReady(seq)` on IPC.

### Frame present (main)

1. On vsync or notify, select newest ready slot.  
2. `GLImage` imports/binds external texture.  
3. Shader applies Scale/Fill/Crop only.

### Stop

1. Stop emitter via bridge.  
2. Release slots / imports.  
3. Clear GLImage present state.

## 4. Phase status

| Phase | Status |
|-------|--------|
| P0 docs | Done |
| P1–P7 | Pending |
