# Implementation Details

## 1. Architecture Overview

```text
AsyncService
  ├─ _pauseEvent   (pause / resume gate before work)
  ├─ _wakeEvent    (interruptible post-work wait)
  ├─ throttle      (live property, seconds)
  └─ _serviceLoop  (while running: wait pause → work → interruptible sleep)
```

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGFx/services/__asyncService.py` | `.docs/jAGFx/services/asyncService.md` | Cooperative async work loop |
| `src/jAGFx/types/interface/services/__services.py` | `.docs/jAGFx/services/` | `iService` protocol |

## 3. Core Workflows & Data Flow

### Normal iteration
1. Await `_pauseEvent` (blocks while paused).
2. Call `await work(...)`.
3. If `throttle > 0`: clear `_wakeEvent`, then `await wait_for(_wakeEvent.wait(), timeout=throttle)`.
4. On timeout → next iteration. On `wake()` → next iteration immediately.

### Dynamic deadline
1. Caller computes a new soonest timeout.
2. Assigns `service.throttle = new_seconds` (setter also calls `wake()`).
3. Pending wait ends; loop re-enters and uses the updated throttle.

### Pause vs wake
- `pause()` only clears `_pauseEvent`.
- `wake()` only sets `_wakeEvent`.
- The two paths never mutate each other's event.
