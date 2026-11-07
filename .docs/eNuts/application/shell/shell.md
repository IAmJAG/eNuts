## Overview & Design Context
`Shell` is the ENUTS main-window application layer. It owns UI composition (WorkSpace as central widget), window settings, and the shared `DeviceManager` used by pages (including K&G Recorder).

* **Design Decision / Deviation Notes:** Recording controller lives **inside** the KG Recorder page. Shell only provides shared services (`DeviceManager`, `settings`, shutdown). Application-level `KGRecorder` has been removed.

---

## Classes

### `Shell`
- **Purpose:** Application shell: settings, window state, device discovery host.
- **Methods:**
  - `_wInitializeUI()` — create `DeviceManager`, install WorkSpace, start discovery.
  - `_wInitializeSettings()` / `_wRestoreWindowsState()` — QSettings lifecycle.
  - `saveWindowState()` / `restoreWindowsState()` — geometry and window state.
  - `closeEvent(event)` — save state, `deviceManager.stopAll()`, set shutdown event.
- **Properties:**
  - `settings` — `QSettings`.
  - `deviceManager` — optional `DeviceManager` / `iDeviceManager` instance.

## Sample Usage

```python
from eNuts.application import Shell
from eNuts.services.device import DeviceManager

# ENUTSWindow(Shell) constructs DeviceManager during workflow InitializeUI:
#   mgr = shell.deviceManager
#   settings = shell.settings
# Pages (e.g. KGRecorder) reach these via shell / mainwindow.
```
