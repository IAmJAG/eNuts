# Stream view, device input, and global devices

**Branch:** `base`  
**Base reference:** `e8cdbf09`  
**Implemented against HEAD at start of work:** `1282d47f`

This document records the phased refactor that separates live image display from device control and registers devices globally on the Shell.

---

## Goals

1. **`imageStreamer`** only paints an image as a background and reports input. It does not decode, own sockets, store device geometry, or inject actions.
2. **Fit on resize** is always on (feature, not a flag).
3. **`iDeviceInputAdapter`** in **fluxCore** abstracts input → device actions so Android, Windows, iOS, or console can each supply a concrete adapter.
4. **Devices are global** on `iShell` (`Devices` / `AddDevice` / `RemoveDevice`), not owned by the recorder page.
5. **Discovery → register → select → bind** is orchestrated by Shell at instance init.
6. **Qt stays out of fluxCore.** Host key/coord mapping lives in eNuts bind helpers.

---

## Phase 1 — Slim `imageStreamer`

**Path:** `src/eNuts/UI/widgets/streamer/__imageStreamer.py`

### Removed

- `Decoder`, `ControlSocket`, `DeviceWidth` / `DeviceHeight`
- `OnFrame` and all decode logic
- `FitOnResize` option (behaviour is mandatory)
- `_C_QT_TO_ANDROID` and all `Touch` / `Scroll` / `InjectKey*` usage

### Added / kept

- `SetStreamingImage(pixmap)` — first frame `resetView`, later frames keep zoom/pan
- `resizeEvent` always refits when a frame is present
- Signals (image-space coords; Qt key + modifiers as ints):
  - `TouchPressed` / `TouchMoved` / `TouchReleased`
  - `WheelScrolled`
  - `KeyPressed` / `KeyReleased`
  - `RightClicked`
- `CaptureInput` still gates whether events are reported

### Result

The widget is a view + input sensor only.

---

## Phase 2 — Device input adapter (fluxCore)

**Paths:**

- `src/fluxCore/types/interface/deviceInput/__deviceInputAdapter.py` — `iDeviceInputAdapter`
- `src/fluxCore/deviceInput/__androidScrcpy.py` — `AndroidScrcpyInputAdapter`

### Protocol

- `Attach(device)` / `Detach()`
- `TouchDown` / `TouchMove` / `TouchUp` (device pixels)
- `Scroll`
- `KeyDown` / `KeyUp` (concrete adapters interpret key types; Android uses `eKeyCode` / `eMetaState`)

### Android concrete adapter

- Reads `ControlSocket`, `width`, `height` from the attached device (e.g. `SCRCPYEmitter`)
- Executes existing fluxCore actions: `Touch`, `Scroll`, `InjectKeyPress`, `InjectKeyRelease`
- No Qt imports

---

## Phase 3 — Shell: discovery, registry, bind

**Paths:**

- `src/eNuts/application/__shell.py`
- `src/eNuts/application/__streamBind.py` — `StreamPipeline` (frame decode + signal wiring)
- `src/eNuts/application/__qtKeyMap.py` — Qt → `eKeyCode` / `eMetaState` (eNuts only)

### Device registry

Implements existing `iShell` surface:

- `Devices` → `Dict[str, iDevice]`
- `AddDevice` / `RemoveDevice`
- `SelectDevice` / `SelectedDevice` (app selection)

### Startup flow (`initializeInstance`)

1. Initialize SideBar (unchanged composition).
2. **Discover** adb serials (`adb.device_list()`).
3. Start a `SCRCPYEmitter` session for preferred serial (`emulator-5560` if present, else first).
4. **Register** via `AddDevice`.
5. **Select** that device.
6. **Bind** `StreamPipeline`:
   - Frame: `ON_FRAME` → decode with device `CodecContext` → `SetStreamingImage`
   - Input: streamer signals → image→device map + Qt key map → `AndroidScrcpyInputAdapter`

Old assignments (`streamer.Decoder = …`, `OnFrame` on the widget) are gone.

---

## Phase 4 — Stabilize

- Grep-clean removed streamer APIs from Shell.
- Package exports for `fluxCore.deviceInput` and `fluxCore.types.interface.deviceInput`.
- This document as the phase log under `.docs/`.

---

## Architecture (after)

```text
adb / discovery
      |
      v
Shell.Devices  (global)
      | select
      v
SCRCPYEmitter session --ON_FRAME--> StreamPipeline.OnFrame
      |                              decode -> SetStreamingImage
      |
      +-- ControlSocket <-- AndroidScrcpyInputAdapter
                                ^
                         StreamPipeline (Qt map + coord map)
                                ^
                         imageStreamer signals
```

Recorder recording (`VARecorder`) is intentionally not wired yet; it will attach to the same selected device and frame bus later.

---

## Naming / style notes

- Class `imageStreamer` remains a lowercase authorized exception.
- Qt overrides keep Qt casing (`mousePressEvent`, etc.).
- Public methods on new types use TitleCase (`SetStreamingImage`, `Attach`, `Bind`).
- Locals use `l` + TitleCase; constants `C_` / `_C_`.
