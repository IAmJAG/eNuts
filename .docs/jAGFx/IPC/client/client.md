# Client — Requirements, Rules, and Mental Model

Parent-side proxy for a single out-of-process worker. Instances are created only by `ProcessHost.start`.

**Location:** `src/jAGFx/IPC/client/__client.py`

This document is the contract. Package-level notes live under `.docs/jAGFx/IPC/`.

---

## 1. Purpose

Represent one child process on the parent side. Own the per-client message queue, heartbeat expiry, and state machine. Domain subclasses (e.g. `DeviceManager`) add domain behavior; the base enforces that instances exist only when started by `ProcessHost`.

---

## 2. Identity

| Fact | Rule |
|------|------|
| Bases | `iClient`, `Subscription` |
| Constructor | `Client(clientId: int)` |
| Creation site | **Only** inside `ProcessHost.start`. Any other call raises `RuntimeError`. |
| Subclassing | Allowed anywhere. The guard runs on instance creation, not class definition. |

---

## 3. Mental model

A `Client` is the parent’s view of one child. `ProcessHost.start` constructs it after the process is spawned and keys it by `process.ident`.

State transitions and the inbound message queue live on the instance. Heartbeats refresh the expiry window; a missed beat marks the client `DORMANT`.

---

## 4. Creation constraint

`_isCalledFromAllowedFactory` inspects the call stack from `__init__`:

- Frame 0: `_isCalledFromAllowedFactory`
- Frame 1: `Client.__init__`
- Frame 2: caller of the constructor

The caller must be a method named `start` whose `self` is an instance of `iProcessHost`. Otherwise the constructor raises.

This replaces the previous (incorrect) check in `__init_subclass__`, which blocked class definition at import time.

---

## 5. Requirements

- Instances may be created only by `ProcessHost.start`.
- Subclasses may be defined in any module; the guard does not run at class-body execution.
- Heartbeat expiry, message queue, and state machine behave as previously implemented.
