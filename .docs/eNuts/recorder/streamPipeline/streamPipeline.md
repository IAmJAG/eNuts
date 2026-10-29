## Overview & Design Context

Cross-process live view: scrcpy in a **client worker**, pixels on a **GPU ring** (design E), UI presents with **GLImage** (shader fit only). Control stays on existing Scrcpy IPC bridges.

* **Design Decision:** Frame plane is GPU interop, not JSON `Message` payloads. System SHM+upload is fallback only.
* **UI Decision:** K&G Recorder stream surface is GLImage; CaptureImage is not used for this path (view-only v1).

See `requirement.md`, `implementationPlan.md`, `implementation.md` in this folder.

---

## Sample mental model

```text
Worker: decode → GPU slot[seq] → RealBridge (control)
Main:   Proxy (control) → import slot → GLImage.presentExternal + fit shader
```
