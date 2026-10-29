# Requirements & Design Specifications — Cross-process stream → GLImage

## 1. Project Overview

Deliver live scrcpy video from a **client worker process** to the **main UI process**, rendered on **GLImage** (K&G Recorder), without putting frame pixels on JSON IPC.

**Primary design:** GPU interop (plane **E**). **View-only v1.**

## 2. Functional Requirements

- **FR-1:** Control plane uses existing Scrcpy IPC bridges.
- **FR-2:** Frame plane is not `Message` JSON; slot header + opaque GPU handles.
- **FR-3:** Client decode + convert to agreed present format; **full frames** after decode (no dirty-rect v1).
- **FR-4:** Main **shader fit only** (Scale/Fill/Crop), including **widget resize** (same texture, new viewport).
- **FR-5:** Ring size 2–4 (default 3); no write/display collision; newest-ready under load.
- **FR-6:** Per-slot header: `magic`, `seq`, `pts`, `w`, `h`, `stride`, `format`, `flags` (see `__frameSlot.py`).
- **FR-7:** KG Recorder surface for this path is **GLImage**.
- **FR-8:** `pts` for later main-side FPS pacing; skip redraw when `seq == lastPresentedSeq`.
- **FR-9:** `flags.RESOLUTION_CHANGED` is a hint; geometry truth is `w`/`h`/`format` on the slot.

## 3. Non-Functional Requirements

- **NFR-1:** Prefer GPU-resident path; no full-frame CPU contract between processes.
- **NFR-2:** One ring per serial; latest-wins.
- **NFR-3:** Docs under `.docs/eNuts/recorder/streamPipeline/` stay in sync.

## 4. Design Decisions

### Full frames after decode

Encoded I/P structure stays in the codec; present plane always carries a full reconstructed surface.

### PTS vs content identity

`pts` paces presentation; `seq` detects same publish. Neither replaces content hashing for “pixels unchanged.”

### GLImage refactor required (P2)

Live path uses external/GPU present API; current `QPainter.drawImage` + CPU scale is not the stream hot path.
