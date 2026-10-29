# Stream Pipeline — Implementation Plan

**Status:** P0–P1 done; P2–P7 pending  
**Branch:** `development`  
**Goal:** Client-process scrcpy → GPU frame plane → main `GLImage` on K&G Recorder (view-only).

**Related:**  
- Control IPC: `.docs/jAGFx/IPC/IPC.md`  
- Scrcpy bridges: `.docs/fluxCore/emitters/scrcpy/` (A–D done)  
- Display: `.docs/jAGQt/widgets/Image/`  
- Slot contract: `frameSlot.md`

---

## Phase status

| Phase | Name | Status |
|-------|------|--------|
| **P0** | Contracts & doc lock | **Done** |
| **P1** | Slot / handle contract + meta header | **Done** |
| **P2** | GLImage external present + shader fit | Pending |
| **P3** | Client producer (decode → GPU slot) | Pending |
| **P4** | Worker host + control IPC session open | Pending |
| **P5** | Main consumer + stream service | Pending |
| **P6** | K&G Recorder UI wire (GLImage) | Pending |
| **P7** | Hardening, multi-device, fallback profile | Pending |

---

## P1 deliverables (done)

| Path | Role |
|------|------|
| `src/fluxCore/emitters/scrcpy/__frameSlot.py` | Header pack/unpack, format/flags, ring helpers, `pts` |
| `.test/smoke/scrcpy/test_frame_slot.py` | Round-trip + ring rules |
| `.docs/eNuts/recorder/streamPipeline/frameSlot.md` | Contract doc |

Header fields: `magic`, `seq`, `pts`, `w`, `h`, `stride`, `format`, `flags` (40 bytes LE).

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

- **IPC:** control + session + optional `FrameReady(seq)`.
- **Pixels:** never on `Message` JSON.
- **Main:** shader fit only (including widget resize).
- **Full frames** after decode; no dirty-rect protocol in v1.

---

## Next: P2 — GLImage external present + shader fit

See prior plan section for files and exit criteria.
