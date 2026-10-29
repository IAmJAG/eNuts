# Requirements & Design Specifications — Cross-process stream → GLImage

## 1. Project Overview

Deliver live scrcpy video from a **client worker process** to the **main UI process**, rendered on **GLImage** (K&G Recorder), without putting frame pixels on JSON IPC.

**Primary design:** GPU interop (plane **E**) — pixels stay GPU-resident when possible; IPC is control/session only.

**View-only v1:** display path only; no CaptureImage / input injection on this surface.

## 2. Functional Requirements

- **FR-1:** Control plane uses existing `jAGFx.IPC` + `ScrcpyRealBridge` / `ScrcpyProxyBridge` (Initialize / Start / Stop / Metadata / Error).
- **FR-2:** Frame plane is **not** `Message` JSON payloads. Contract is GPU ring slots (or documented fallback) + small metadata.
- **FR-3:** Client performs decode and any format conversion to an **agreed present format** at stream open.
- **FR-4:** Main performs **shader fit only** (Scale / Fill / Crop). No decode on main.
- **FR-5:** Ring length **2–4** (default **3**). No write/display collision; live view uses **newest ready** slot (drop under load).
- **FR-6:** Per-slot header carries `seq`, `w`, `h`, stride, format, flags for present. IPC carries session setup and rare resolution changes.
- **FR-7:** K&G Recorder display surface for this path is **GLImage**, not CaptureImage.
- **FR-8:** Hot path target: no full-frame CPU buffer as the inter-process contract; no GPU→CPU readback as the primary design.

## 3. Non-Functional Requirements

- **NFR-1:** Latency — prefer GPU decode + import over SHM upload.
- **NFR-2:** Scalability — one ring (or handle set) per `serial`; latest-wins under UI backpressure.
- **NFR-3:** Portability — E may be platform-specific; a SHM+upload **fallback profile** may exist but is not the design center.
- **NFR-4:** Docs under `.docs/eNuts/recorder/streamPipeline/` stay in sync with implementation phases.

## 4. Design Decisions

### E over C for the primary plane

- **Affected:** frame transport, GLImage, worker, KG Recorder attach path.
- **Decision:** GPU interop is the primary pixel path; system SHM is fallback only.
- **Justification:** lowest latency when frames never bounce through system RAM.

### Main processing limited to shader fit

- **Affected:** `GLImage`, recorder UI.
- **Decision:** Scale/Fill/Crop in shader only on main.
- **Justification:** isolates all heavy work on the client; UI process stays present-only.

### GLImage must be refactored for live streams

- **Affected:** `src/jAGQt/widgets/Image/__glImage.py`, `ImageBase` usage for live path.
- **Decision:** Live path uses external/GPU present API; current `QPainter.drawImage` + CPU scale is not the stream hot path.
- **Justification:** current GLImage is QOpenGLWidget + CPU blit, not interop-ready.
