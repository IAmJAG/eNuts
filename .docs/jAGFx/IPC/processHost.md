# ProcessHost — Requirements, Rules, and Mental Model

Parent-side host for named out-of-process workers. Heavy work runs in one or more child processes. The parent (normally the UI event loop) stays responsive.

Location: `src/jAGFx/IPC/__processHost.py`

This document states the contract. As-built notes are `implementation.md`.

---

## 1. Purpose

Move heavy work off the main process. Give the parent a way to talk to those processes, and a way to shut them down without leaking processes, queues, or tasks.

This is a pure IPC primitive. It does not carry device identity or SCRCPY options.

---

## 2. Identity

| Fact | Rule |
|------|------|
| Base | `AsyncProcess` (events + name) |
| Worker | Module-level coroutine. Default `_clientWorker`. |
| Name | Optional host name for logging / process naming. |

Domain workers (e.g. `SCRCPYWorker`) are supplied via `worker=`.

---

## 3. Mental model

One parent. Many clients. Two directions of traffic. The parent owns every queue.

- **Parent → client.** One outbound queue per client (`_outQueues[clientId]`). That queue is the client's inbound.
- **Client → parent.** One inbound queue on the parent (`_inQueue`). Shared by every client.
- **Shutdown.** One shared event. Setting it tells every client and the parent receiver to stop.

```text
parent _dispatch(clientId) ──► _outQueues[clientId] ──► that client only
any client put             ──► _inQueue              ──► parent receiver
```

---

## 4. Requirements (summary)

- `start(clientId)` requires a running event loop; fails before side effects if none.
- Duplicate `clientId` is rejected.
- First start creates shared inbound + shutdown event.
- Each start creates one dedicated outbound queue and a daemon process `PROC_{clientId}`.
- Worker must be a module-level coroutine (spawn-safe).
- Failed start rolls back what it created.
- `stop` coalesces; `waitStopped` awaits the retained task.
- Shutdown order: ON_STOPPING → set event → finish receiver → join/kill processes → close queues → ON_STOPPED.
- `running()` / `running(clientId)` report process + shutdown state.

---

## 5. Acceptance

`src/TEST/smoke/ipc/processHost.py`

```text
py .\src\main.py --module TEST --app smoke.ipc.processHost
```
