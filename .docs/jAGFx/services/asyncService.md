## Overview & Design Context

`AsyncService` provides a cooperative asynchronous work loop with an optional
throttle and two distinct control events.

* **Design Decision:** The service exposes a live `throttle` property and a
  `wake()` method so callers (for example correlation timeout trackers) can
  change the post-work wait duration and force an early re-evaluation without
  stopping the service. Existing consumers that never write `throttle` or call
  `wake()` retain the original fixed-throttle behaviour.

---

## Classes

### `AsyncService`
- **Purpose:** Run an awaitable `work` callable in a loop, optionally sleeping
  after each iteration. Supports pause/resume and dynamic throttle with early
  wake.
- **Methods:**
  - `start(*args, **kwargs)` -> Start the service loop (raises if already running).
  - `stop(forceAfter=0.1)` -> Request cooperative stop; force-cancel after the
    given delay if the task does not finish.
  - `pause()` -> Clear the pause event so the loop suspends before the next work.
  - `resume()` -> Set the pause event so the loop may continue.
  - `wake()` -> Set the wake event so a pending throttle wait ends early.
  - `throttle` (property) -> Get or set the post-work wait in seconds. Setting
    a new value also calls `wake()`.

---

## Constants & Globals

### `C_DEFAULT_FORCE_AFTER`
- **Type:** `float`
- **Value / Description:** Default delay (0.1 s) before `stop` force-cancels
  the service task.

## Sample Usage

```python
from jAGFx.services import AsyncService

async def myWork() -> None:
    ...

svc = AsyncService(work=myWork, name="example", throttle=1.0)
svc.start()

# Later: shorten the wait and force the loop to notice immediately
svc.throttle = 0.05
# or just
svc.wake()

svc.stop()
```

---

## Pause Event vs Wake Event

| Aspect | `_pauseEvent` | `_wakeEvent` |
|--------|---------------|--------------|
| Purpose | Long-lived pause / resume control | Short-lived throttle / deadline interrupt |
| Cleared by | `pause()` | Immediately before a throttle wait |
| Set by | `resume()`, `start()`, `stop()` | `wake()`, throttle setter, `start()`, `stop()` |
| Affects | Whether the loop is allowed to run `work` | Whether the current post-work sleep ends early |
| Typical caller | External control (UI, supervisor) | Internal scheduling (timeout trackers, dynamic deadlines) |

The two events are independent. Pausing the service does not clear the wake
event, and calling `wake()` never resumes a paused service.
