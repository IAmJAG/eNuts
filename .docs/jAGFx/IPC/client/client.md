# Client — Requirements, Rules, and Mental Model

Parent-side proxy for a single out-of-process worker. Instances MUST be created only by `ProcessHost.start`.

**Location:** `src/jAGFx/IPC/client/__client.py`

This document is the contract. Package-level notes live under `.docs/jAGFx/IPC/`.

---

## 1. Purpose

Represent one child process on the parent side. Own the per-client message queue, heartbeat expiry, and state machine. Domain subclasses (e.g. `DeviceManager`) add domain behavior; the base enforces that instances MUST exist only when started by `ProcessHost`.

---

## 2. Identity

| Fact | Rule |
|------|------|
| Bases | `iClient`, `Subscription` |
| Metaclass | `_ClientMeta` (intercepts every construction) |
| Constructor | `Client(clientId: int)` |
| Creation site | **MUST** be inside `ProcessHost.start`. Any other call raises `RuntimeError`. |
| Subclassing | Class definition is unrestricted. Instantiation of any subclass is still gated by the metaclass. |

---

## 3. Mental model

A `Client` is the parent’s view of one child. `ProcessHost.start` constructs it after the process is spawned and keys it by `process.ident`.

State transitions and the inbound message queue live on the instance. Heartbeats refresh the expiry window; a missed beat marks the client `DORMANT`.

---

## 4. Creation constraint (MUST)

Every construction of `Client` or any subclass goes through `_ClientMeta.__call__`, which calls `_isCalledFromAllowedFactory`.

The stack walk expects:

- Frame 0: `_isCalledFromAllowedFactory`
- Frame 1: `_ClientMeta.__call__`
- Frame 2: caller of the constructor

The caller MUST be a method named `start` whose `self` is an instance of `iProcessHost`. Otherwise construction raises.

No subclass can bypass the guard by omitting `super().__init__`.

---

## 5. Requirements

- Instances of `Client` and every subclass MUST be created only by `ProcessHost.start`.
- Subclasses may be defined in any module; the guard runs at instantiation, not at class-body execution.
- Heartbeat expiry, message queue, and state machine behave as previously implemented.
