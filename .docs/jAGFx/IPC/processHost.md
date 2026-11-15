# ProcessHost — Requirements, Rules, and Mental Model

Parent-side host for named out-of-process workers. Heavy work runs in one or more child processes. The parent (normally the UI event loop) stays responsive.

**Location:** `src/jAGFx/IPC/__processHost.py`  
**Workers:** `src/jAGFx/IPC/__workers.py`  
**Acceptance:** `src/TEST/smoke/ipc/processHost.py`

This document is the contract. Package-level notes live under `.docs/jAGFx/IPC/`.

---

## 1. Purpose

Move heavy work off the main process. Give the parent a way to talk to those processes, and a way to shut them down without leaking processes, queues, or tasks.

`ProcessHost` is a pure IPC primitive under `jAGFx.IPC`. It does **not** carry device identity, SCRCPY options, or fluxCore types. Domain behavior is supplied only as a module-level worker coroutine.

---

## 2. Identity

| Fact | Rule |
|------|------|
| Base | `AsyncProcess` (subscription events + name) |
| Constructor | `ProcessHost(name=None, worker=None)` |
| Default worker | `clientWorker` when `worker` is omitted |
| Domain workers | Passed explicitly, e.g. `worker=SCRCPYWorker` or `worker=echoWorker` |
| Worker rule | Must be a **module-level** coroutine (spawn-safe). Not a method, not nested. |

---

## 3. Mental model

**One parent. Many named clients. Two directions of traffic. The parent owns every queue.**

### Topology

| Direction | Structure | Attribute |
|-----------|-----------|-----------|
| Parent → client | One dedicated outbound queue per `clientId` | `_outQueues[clientId]` |
| Client → parent | One shared inbound queue for all clients | `_inQueue` |
| Shutdown | One shared event observed by every child and the parent receiver | `_shutdownEvent` |
| Parent receive | One asyncio task on the shared inbound | `_receiverTask` |
| Children | One daemon process per client, named `PROC_{clientId}` | `_processes[clientId]` |

From the **parent** view:

- `_outQueues[clientId]` is outbound to that client only.
- `_inQueue` is the single inbound from every client.

From the **client** view:

- Its inbound is the queue the parent stored under `_outQueues[clientId]`.
- Its outbound is the parent’s `_inQueue`.

### Message path

```text
parent._dispatch(clientId, msg)
        │
        ▼
_outQueues[clientId]  ──►  that client’s worker only

client worker put
        │
        ▼
_inQueue (shared)     ──►  parent._receiver
```

Addressed parent→client; shared client→parent. No broadcast to every client.

### Ownership

- Parent creates and closes every queue.
- Parent creates and joins/kills every process.
- Worker closes **only** its dedicated inbound on exit.
- Worker must **not** close the shared outbound (`_inQueue`); that would cut off other clients.
- Parent receiver is one task for the whole host; first successful path that needs it starts it; stop finishes it.

### Lifecycle sketch

```text
start(clientId)
  reject if clientId already running
  ensure shared shutdown event + shared inbound exist
  create dedicated outbound for clientId
  spawn PROC_{clientId} with (clientId, event, clientQueue, sharedQueue)
  ensure parent receiver task is running on shared inbound

stop / stopAsync
  ON_STOPPING
  set shared event
  finish parent receiver
  join each child (terminate/kill if forced or still alive)
  close all queues, clear state
  ON_STOPPED
```

---

## 4. Requirements

### 4.1 Startup

- `start(clientId)` requires a running asyncio event loop. Without one it must fail **before** creating processes or queues (via `createTask` / loop use).
- A `clientId` that is already started is rejected (`RuntimeError`).
- Shared inbound and shared shutdown event are created once and reused for later clients.
- Each start creates one dedicated outbound queue and one daemon process `PROC_{clientId}`.
- The parent has a single receiver on `_inQueue`, shared by all clients.
- The child target is the module-level worker passed to the constructor (default `clientWorker`).
- A failed start must not leave an orphaned process or an open queue for that client. If no clients remain, shared inbound and shutdown event are released.

### 4.2 Messaging

- Parent sends with `_dispatch(clientId, msg)` (put off the loop via `to_thread`).
- A client reads only its own inbound; it does not see another client’s traffic.
- A client writes only to the shared outbound (`_inQueue`).
- Payloads are opaque. Base workers print or echo; interpretation belongs to a supplied worker or a subclassed `_receiver`.

### 4.3 Shutdown

- One shared event stops every client and the parent receiver.
- `stop` with a running loop schedules one retained `stopAsync` task. A second `stop` while that task is running is a no-op.
- `stop` with no running loop runs `_stopSync`.
- `waitStopped` awaits the retained stop task if present.
- Order: `ON_STOPPING` → set event → finish receiver → join/kill processes → close queues → `ON_STOPPED`.
- Cleanup runs even if a step fails.
- Queue close cancels the feeder thread so closed queues do not leave background threads.

### 4.4 Liveness

- `running()` — true only when the shutdown event exists, is not set, and process count > 0.
- `running(clientId)` — true only when that client’s process exists and is alive.

Liveness is process + shutdown state, not “receiver healthy” or “queue open.”

### 4.5 Events

Raised exactly once per stop cycle:

- `ON_STOPPING`
- `ON_STOPPED`

---

## 5. Worker policy

| Worker | Role |
|--------|------|
| `clientWorker` | Default dummy: reads inbound, prints, closes inbound on exit |
| `echoWorker` | Smoke/acceptance: echoes `FROM {clientId}:{msg}` to shared outbound |
| `SCRCPYWorker` | Domain worker for SCRCPY serial sessions; not the default |

Rules:

- Workers are module-level coroutines in `__workers.py`.
- Signature: `(clientId, shutdownEvent, inQueue, outQueue, *args, **kwargs)`.
- Spawn imports the worker by name through `processEntry`. The host imports the worker; the worker does not import the host.
- On exit the worker closes only its dedicated inbound.

---

## 6. Acceptance

```text
py .\src\main.py --module TEST --app smoke.ipc.processHost
```

Checks: no-loop start creates nothing; addressed round-trips; duplicate client rejected; stop coalesces; `ON_STOPPING` then `ON_STOPPED`; queues cleared.
