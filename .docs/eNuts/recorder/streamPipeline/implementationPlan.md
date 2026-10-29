# Stream Pipeline — Implementation Plan

**Status:** Planned  
**Branch:** `development`  
**Goal:** Client-process scrcpy → GPU frame plane → main `GLImage` on K&G Recorder (view-only).

**Related:**  
- Control IPC: `.docs/jAGFx/IPC/IPC.md`  
- Scrcpy bridges: `.docs/fluxCore/emitters/scrcpy/` (A–D done)  
- Display: `.docs/jAGQt/widgets/Image/`

---

## Phase status

| Phase | Name | Status |
|-------|------|--------|
| **P0** | Contracts & doc lock | **This document** |
| **P1** | Slot / handle contract + meta header | Pending |
| **P2** | GLImage external present + shader fit | Pending |
| **P3** | Client producer (decode → GPU slot) | Pending |
| **P4** | Worker host + control IPC session open | Pending |
| **P5** | Main consumer + stream service | Pending |
| **P6** | K&G Recorder UI wire (GLImage) | Pending |
| **P7** | Hardening, multi-device, fallback profile | Pending |

---

## Architecture (locked)

```text
CLIENT                              MAIN
SCRCPY → HW decode (prefer)
      → agreed present format
      → GPU ring [2..4] + slot header
      → publish seq
RealBridge + Endpoint ──IPC──► Proxy + Endpoint
      GPU interop handles ──► GLImage.presentExternal + shader fit
                              KG Recorder surface
```

- **IPC:** control + session (format, ring N, handles/fds) + optional `FrameReady(seq)`.
- **Pixels:** never on `Message` JSON.
- **Main image work:** shader fit only.

---

## P0 — Contracts (done when this doc lands)

**Deliverables**

- `requirement.md`, `implementationPlan.md`, `implementation.md` under `.docs/eNuts/recorder/streamPipeline/`
- Cross-links from scrcpy plan + IPC.md

**No code required.**

---

## P1 — Slot / handle contract

**Goal:** Define the binary/API contract both processes implement.

| Item | Detail |
|------|--------|
| Ring size | Default 3; configurable 2–4 |
| Slot header | magic, seq, w, h, stride, format, flags |
| Present format | Agreed at `openStream` (platform fourcc / RGBA / NV12) |
| Import handle | Opaque platform handle (DMABUF fd, shared texture name, etc.) |
| Rules | No write on display index; main shows newest ready; drop under load |

**Files (expected)**

| Path | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/__frameSlot.py` (or `src/jAGFx/IPC/frame/`) | Header struct, format enum, ring index helpers |
| `.docs/eNuts/recorder/streamPipeline/frameSlot.md` | Contract doc |

**Exit:** Unit/smoke that packs/unpacks header; no Qt required.

---

## P2 — GLImage external present + shader fit

**Goal:** Live path does not use per-frame `QPixmap` / `QPainter.drawImage`.

| Path | Action |
|------|--------|
| `src/jAGQt/widgets/Image/__glImage.py` | `presentExternal` / texture bind; shader Scale\|Fill\|Crop |
| `src/jAGQt/widgets/Image/__imageBase.py` | Keep static `image` for non-stream; live path separate |
| `.docs/jAGQt/widgets/Image/glImage.md` | Document present API |
| `.docs/jAGQt/widgets/Image/requirement.md` / `implementation.md` | Update |

**Exit:** Synthetic texture or static GPU buffer presented with fit modes; resize stable.

**Note:** Platform interop import can be stubbed with a locally created texture until P3/P4 supply real handles.

---

## P3 — Client producer

**Goal:** After decode, publish into ring slots (GPU-first).

| Path | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/` producer module | ON_FRAME / codec output → convert → write slot + header → publish |
| Wire from `SCRCPYEmitter` or RealBridge Start | Subscribe once stream open |

**Exit:** Logs/metrics show advancing `seq`; optional single-process test with GLImage stub.

**Dependency:** HW decode path may land incrementally; software decode must not define the inter-process **contract** as CPU frames (if SW is used temporarily, document as non-goal path).

---

## P4 — Worker host + session IPC

**Goal:** Client process runs emitter + RealBridge; main opens stream session.

| Path | Action |
|------|--------|
| Worker entry (e.g. `src/eNuts/application/ipc/scrcpyWorker.py`) | Endpoint, RealBridge, emitter, frame producer |
| Session messages or openStream API | Share ring N, format, import handles/fds |
| Optional `FrameReady(seq)` message | Tiny; pixels still not on queue |
| `AsyncProcess` (or host) | Lifecycle |

**Exit:** Main Initialize/Start over existing bridges; worker publishes slots; main can import (even if UI not wired).

---

## P5 — Main consumer + stream service

**Goal:** Abstract what KGRecorder needs without holding local `SCRCPYEmitter` for frames.

| Path | Action |
|------|--------|
| `iDeviceStream` / `IpcDeviceStream` (e.g. under `src/eNuts/application/`) | open/start/stop; on-frame → present |
| ScrcpyProxyBridge + consumer | Map seq → GLImage.presentExternal |
| deviceManager integration | Factory for ipc vs local later |

**Exit:** Headless or minimal window shows stream from worker via GLImage.

---

## P6 — K&G Recorder UI

**Goal:** User-visible path.

| Path | Action |
|------|--------|
| Playback / KG page surface | **GLImage** instead of CaptureImage for stream view |
| `src/eNuts/application/recorder/__kgRecorder.py` | Attach `iDeviceStream`; remove in-process decode→QImage hot path for IPC mode |
| Shell startup | Start worker + endpoints when IPC stream mode enabled |

**Exit:** Select device on KG Recorder → live frames on GLImage while emitter runs in worker process.

**Explicitly deferred in P6:** mouse/key injection on this surface; recording file format.

---

## P7 — Hardening

- Multi-serial stream table  
- Worker crash → proxy error → status text  
- Stop/detach releases GPU slots and GL imports  
- Fallback profile (SHM+upload) behind flag, same header contract where possible  
- Backpressure metrics (dropped seq)  

---

## File impact summary (by phase)

| Phase | Primary touch set |
|-------|-------------------|
| P1 | `fluxCore` or `jAGFx` frame slot contract + docs |
| P2 | `jAGQt/widgets/Image/*` + Image docs |
| P3 | `fluxCore/emitters/scrcpy/*` producer |
| P4 | `eNuts/application/ipc/*`, process host |
| P5 | `eNuts/application` stream service, proxy consumer |
| P6 | `eNuts/UI/pages`, `recorder/__kgRecorder.py`, shell |
| P7 | Same + flags/metrics |

---

## Ordering rules

1. Do not put RGB/H264 payloads on `Message`.  
2. Do not make SHM+CPU upload the primary contract.  
3. GLImage live path before full UI wire (P2 before P6).  
4. One phase per commit group with matching `.docs` updates.  
5. Run `.scripts/updateInventory.py` after code phases that add modules.

---

## Acceptance (program level)

- [ ] Worker process owns `SCRCPYEmitter`  
- [ ] Main process presents via refactored `GLImage`  
- [ ] KG Recorder shows live view without CaptureImage on this path  
- [ ] Control remains on existing Scrcpy IPC bridges  
- [ ] No full-frame JSON; no required GPU→CPU readback on the happy path  
