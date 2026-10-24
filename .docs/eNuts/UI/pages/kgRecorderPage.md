## Overview & Design Context
Factory `buildKGRecorderPage` builds the Key & Gesture Recorder page as a pure view: CaptureImage (stream + event source), expandable configuration strip (device combo first), status label, event list, and CommandBar (Start/Stop, Clear, Save/Open).

* **Design Decision / Deviation Notes:** Recording logic lives outside the Page in `KGRecorder` (ENUTSWindow component, wired from Shell). The page never owns session state. CaptureImage is a plain event source with no recording logic.

---

## Functions

### `buildKGRecorderPage`
- **Arguments:** `key` (str) - Page id; defaults to `PAGE_KG_RECORDER`.
- **Returns:** `Page` - Fully composed recorder page.
- **Behavior:** Creates `Page` with CommandBar enabled, lays out CaptureImage on the left and config/status/event list on the right, registers CommandBar groups, and stashes `_captureImage`, `_deviceCombo`, `_statusLabel`, `_eventList`, `_configStrip` on the page for the controller.

---

## Constants & Globals

None beyond page-key usage from `__pageKeys`.

## Sample Usage

```python
from eNuts.UI.pages import buildKGRecorderPage, PAGE_KG_RECORDER

page = buildKGRecorderPage(PAGE_KG_RECORDER)
```
