# Requirements & Design Specifications

## 1. Project Overview

`AsyncService` is the standard cooperative async work-loop primitive used across
jAGFx. It must support both simple fixed-rate polling and dynamic deadline
scheduling (for example Bridge correlation timeout trackers).

## 2. Functional Requirements

- **FR-1:** The service runs an awaitable `work` callable in a loop while
  `isRunning` is true.
- **FR-2:** After each successful `work` invocation the service may wait up to
  `throttle` seconds before the next iteration.
- **FR-3:** `throttle` is exposed as a read/write property. Setting a value
  less than zero raises `ValueError`. Setting a new value wakes any pending
  wait so the new duration is observed promptly.
- **FR-4:** `wake()` ends a pending throttle wait early without affecting the
  pause/resume state.
- **FR-5:** `pause()` / `resume()` control a separate long-lived event that
  suspends the loop *before* the next `work` call.
- **FR-6:** Existing callers that never write `throttle` after construction and
  never call `wake()` must observe behaviour identical to the previous
  fixed-sleep implementation.

## 3. Non-Functional Requirements

- **NFR-1:** The wait must be interruptible; a newly registered shorter deadline
  must not wait out a previous long sleep.
- **NFR-2:** No busy-loop when `throttle == 0.0` beyond the historical semantics.
- **NFR-3:** Force-stop via `stop(forceAfter=...)` remains available.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Separate pause and wake events
- **Affected Modules:** `src/jAGFx/services/__asyncService.py`
- **Description of Standard / Best Practice:** A single Event is sometimes used
  for both suspension and notification.
- **Divergence:** Two distinct `asyncio.Event` instances are kept:
  - `_pauseEvent` for cooperative pause/resume
  - `_wakeEvent` for early termination of the post-work throttle wait
- **Design Decision & Justification:** The two signals have different lifetimes
  and different callers. Mixing them would make it easy for a wake intended only
  to refresh a deadline to accidentally resume a paused service (or vice-versa).
- **Code Doc Cross-Reference:** See the table in `asyncService.md`.
