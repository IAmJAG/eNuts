# Ground-up rebuild — startup

**Branch:** `base`  
**Goal:** prove a flicker-free window, then re-add one layer at a time.

## Layer 0 (current)

- `MainWindow`: `MainWindowBase` + `ApplicationInformation` only  
- **No** `@workflow`  
- **No** `Shell` mixin  
- **No** SideBar / Workspace / streamer / devices  
- `main`: style → construct → `show()` → wait quit  
- **No** `sleep`, **no** `initializeInstance`

**Pass criteria:** one window appears; no extra flashes; no second window in the taskbar.

## Layer plan

| Layer | Add | Still forbidden |
|------|-----|-----------------|
| **L1** | Sync settings + restore geometry (same thread, before show) | Signal/workflow chain |
| **L2** | Central layout + single `QLabel` / frame | SideBar, pages |
| **L3** | SideBar only | Workspace, stream |
| **L4** | Workspace + pages | Streamer, devices |
| **L5** | imageStreamer in Recorder page | Device session |
| **L6** | post-show discover → session → StreamPipeline | Workflow decorator |

Rules for every layer:

1. All UI build is **synchronous** on the GUI thread **before** `show()`.  
2. Anything `await`ed runs **after** `show()` and must not create/reparent shell chrome.  
3. If flicker returns, the last layer is the suspect — revert it before adding more.

## Intentionally parked

- `@workflow` / jAGQtFx chain signals (until DirectConnection is proven)  
- Full Shell UI builders (reintroduce per layer)  
- Device pipeline until L6
