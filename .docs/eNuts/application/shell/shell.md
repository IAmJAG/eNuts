## Overview & Design Context
`Shell` is the ENUTS main-window application layer. It owns UI composition (WorkSpace as central widget), window settings, and the device/recorder stack used by K&G Recorder.

* **Design Decision / Deviation Notes:** `deviceManager` and application-level `KGRecorder` are created once in `_ensureManagers` during `_wInitializeUI`, then the KG recorder page is bound after WorkSpace registers pages. Ownership lives on Shell (not on the Page).

---

## Classes

### `Shell`
- **Purpose:** Application shell: settings, window state, device discovery host, KGRecorder host.
- **Methods:**
  - `_ensureManagers()` — create `deviceManager` + `KGRecorder` once; wire `setDeviceManager`; schedule discovery.
  - `_bindKgRecorderPage(workspace)` — bind application `KGRecorder` to the `PAGE_KG_RECORDER` page instance.
  - `_wInitializeUI()` — ensure managers, install WorkSpace, bind KG page.
  - `_wInitializeSettings()` / `_wRestoreWindowsState()` — QSettings lifecycle.
  - `saveWindowState()` / `restoreWindowsState()` — geometry and window state.
  - `closeEvent(event)` — save state, `deviceManager.stopAll()`, set shutdown event.
- **Properties:**
  - `settings` — `QSettings`.
  - `deviceManager` — optional `deviceManager` instance.
  - `KGRecorder` — optional application `KGRecorder` controller.

## Sample Usage

```python
from eNuts.application import Shell
# ENUTSWindow(Shell) constructs managers during workflow InitializeUI:
#   mgr = shell.deviceManager
#   rec = shell.KGRecorder
#   rec.setDeviceManager(mgr)  # already done by Shell
```
