# outOfProcessEmitter — Requirements, Rules, and Mental Model

Out-of-process emitter base. Heavy work runs in one or more child processes. The parent (normally the UI event loop) stays responsive.

This document states the contract. As-built notes are `implementation.md`.

---

## 1. Purpose

Move a heavy method off the main process. Give the parent a way to talk to those processes, and a way to shut them down without leaking processes, queues, or tasks.

---

## 2. Identity

| Fact | Rule |
|------|------|
| Bases | `AsyncProcess`, `SCRCPY` |
| Protocol | Satisfies `iSCRCPYEmitter` structurally. It is not an explicit base. |
| Device identity | Carries a SCRCPY serial and optional name. |
| Options | Optional `SCRCPYOptions`. |
| Worker | Optional module-level coroutine. Default is `_clientWorker`. |

The protocol is structural because the three interface orders cannot be linearized together: `SCRCPY` contributes `iDevice` early, `AsyncProcess` contributes `iSubscription` before `iService`, and `iEmitter` wants `iService`, then `iSubscription`, then `iDevice`.

---

## 3. Mental model

One parent. Many clients. Two directions of traffic. The parent owns every queue.

- **Parent → client.** One outbound queue per client (`_outQueues[clientId]`). That queue is the client's inbound. The parent writes to a specific client. Clients do not compete.
- **Client → parent.** One inbound queue on the parent (`_inQueue`). That queue is the clients' single shared outbound. Every client writes to it. The parent has one receiver on it.
- **Shutdown.** One shared event. Setting it tells every client and the parent receiver to stop.
- **`_clientWorker`.** The only code that runs in a client. A module-level coroutine in its own module, given that client's queues.

A client is identified by `clientId`. Starting the same id twice is an error. Starting the first client creates the parent's shared inbound queue and the shared shutdown event. Each start creates that client's dedicated outbound queue and a daemon process named `PROC_{clientId}`. Later clients reuse the shared inbound queue and the event.

Message travel:

```text
parent _dispatch(clientId) ──► _outQueues[clientId] ──► that client only
any client put             ──► _inQueue              ──► parent receiver
```

Ownership, named from the parent:

| Queue | Parent sees it as | Client sees it as | Cardinality |
|-------|-------------------|-------------------|-------------|
| `_outQueues[clientId]` | outbound to that client | its inbound | one per client |
| `_inQueue` | the inbound | its outbound | one for all clients |

---

## 4. Requirements

### 4.1 Startup

- `start(clientId)` requires a running event loop. If there is none, it fails before any process or queue is created.
- A `clientId` that is already started is rejected.
- The first successful start creates the parent's shared inbound queue and the shared shutdown event.
- Each start creates one child process and one dedicated outbound queue for that client.
- The parent has one receiver on the shared inbound queue. It is started with the first client and serves every client.
- Child processes are daemons, named `PROC_{clientId}`.
- The child target is a module-level coroutine. Default is `_clientWorker`. A method or a nested function is not acceptable.
- If start fails after resources were created, those resources are released. A failed start does not leave an orphaned process or an open queue. If the failure leaves zero clients, the shared inbound queue and the shutdown event are released too.

### 4.2 Messaging

- The parent sends with `_dispatch(clientId, msg)`, which puts on that client's dedicated outbound queue, off the loop.
- A client receives only from its own inbound queue. It does not see another client's traffic.
- A client sends to the parent by putting on the shared outbound queue.
- The parent receives every client's messages on its single inbound receiver.
- Payloads are opaque. The base worker prints the message. A different module-level worker replaces that observation.
- Parent-to-client delivery is addressed, not competing. Client-to-parent delivery is shared.

### 4.3 Shutdown

- One shared event stops every client and the parent receiver.
- `stop` with a running loop schedules an asynchronous stop and returns. The scheduled task is retained. A second `stop` while that task is running does nothing.
- `stop` with no running loop performs a synchronous stop.
- `stopAsync` performs the full sequence and can be awaited.
- `waitStopped` awaits the retained stop task if one exists.
- Shutdown order:
  1. Raise `ON_STOPPING`.
  2. Set the shared event.
  3. Finish the parent receiver (it exits because the event is set; the no-loop path cancels it).
  4. Join each child. If `forced`, terminate first. If still alive after the timeout, terminate, then kill.
  5. Close every queue and clear client state.
  6. Raise `ON_STOPPED`.
- Cleanup runs even if a step fails.
- Queue close includes cancelling the feeder thread, so a closed queue does not leave a background thread behind.

### 4.4 Liveness

`running` has two forms.

- **`running()` — no argument.** True only when all of these hold:
  - the shutdown event exists,
  - the shutdown event is not set,
  - the process count is greater than zero.
- **`running(clientId)` — with a client id.** True only when that client's process exists and is alive.

Liveness is process and shutdown state. It does not mean a receiver is healthy or a queue is open. A set shutdown event makes the no-argument form false even if a process has not yet exited.

### 4.5 Events

Lifecycle notifications that must be raised exactly once per stop:

- `ON_STOPPING`
- `ON_STOPPED`

---

## 5. `_clientWorker` — rule and policy

`_clientWorker` is the child entry. It is the only code that runs inside a client process.

### Rule

- It is a module-level coroutine in `src/fluxCore/emitters/__clientWorker.py`.
- It is not a method of `outOfProcessEmitter`. It is not a nested function. It is not a bound method.
- Spawn imports it by name from that module. The child process loads the worker module, not the emitter class.
- It receives the shutdown event, that client's inbound queue, and the shared outbound queue. It does not receive the emitter.
- It exits when the event is set. It does not own process lifetime.
- It reads only its inbound queue and writes only the shared outbound queue.
- On exit it closes only its dedicated inbound. It does not close the shared outbound.

### Why it must be module level

Windows starts children with `spawn`, not `fork`. The child is a new interpreter. It rebuilds the process target by importing it.

- A nested function has no import path. Spawn fails with `Can't get local object`.
- A bound method pickles the emitter. That pulls in the parent, its other process handles, and its queues. That is forbidden.
- A module-level function has a stable import path: `module._clientWorker`. Spawn imports that and calls it.

### Why its own module

The emitter module imports the device, the process base, and the parent class. The child does not need any of that. A separate worker module means the child imports only the worker. The emitter imports the worker. The worker does not import the emitter.

### Policy

- One worker for every client. Per-client state is the queues it is given, not a different function.
- The base worker prints a message. A different module-level worker is passed as `worker=`. Not a method override.
- On exit the worker closes its dedicated inbound only. The parent closes the shared inbound and every outbound queue.
- A failing worker does not skip that close. The parent still reaps the process.

---

## 6. Rules

| Rule | Meaning |
|------|---------|
| Loop before side effects | No process, queue, or task is created until a running loop is confirmed. |
| One owner per client id | A second `start` for the same id fails. |
| Shared in, private out | Parent→client is dedicated per client. Client→parent is one shared queue. |
| Spawn-safe worker | `_clientWorker` is a module-level coroutine in its own module. Not a method. Not nested. |
| Worker closes its inbound only | The shared outbound stays open until the parent closes it. |
| Cooperative first | Shutdown is signaled by the event. Force is an explicit option. |
| No early close | Queues stay open until the parent receiver has finished and processes have been joined. |
| No leaked handle | Every started process is joined or killed, then closed. Every created queue is closed. |
| Coalesced stop | A stop already in flight is not started again. |
| Observable stop failure | A failure in the scheduled stop is reported, not swallowed. |
| Structural protocol | `iSCRCPYEmitter` is satisfied by shape, not by inheritance. |
| Parent stays on the loop | Blocking queue waits run off the event loop. |

---

## 7. Policies

**Worker policy.** `_clientWorker` is the child. It is one module-level coroutine in its own module, shared by every client, given that client's inbound queue and the shared outbound queue. It observes the shutdown event and exits. It closes only its inbound. It does not own the process, the event, or the parent's queues. The emitter imports the worker. The worker does not import the emitter.

**Process policy.** Children are daemons named `PROC_{clientId}`. They exit when the parent exits. They are still explicitly joined on stop so handles and feeder threads are released.

**Failure policy.** A failed start rolls back only what that start created. Shared resources are dropped only when the last client is gone.

**Timeout policy.** Stop waits up to the default stop timeout, then escalates to terminate, then to kill. The kill join is short.

**Message policy.** The base emitter does not interpret payloads. It transports them. Interpretation belongs to a supplied worker or a subclass receiver.

**Concurrency policy.** The parent receiver is an asyncio task on the parent's loop. `_clientWorker` is an asyncio coroutine inside the child process. The two sides share only queues and the shutdown event.

---

## 8. Available technology

| Layer | What is available | Role |
|-------|-------------------|------|
| Language runtime | Python `asyncio` | Parent loop, child loop, tasks, `to_thread` |
| Process | `multiprocessing.Process` | Child process |
| Signal | `multiprocessing.Event` | Shared shutdown |
| Transport | `multiprocessing.Queue` | Cross-process messages |
| Empty signal | `queue.Empty` | Timed gets |
| Process base | `jAGFx.services.AsyncProcess` | Name, events |
| Spawn entry | `jAGFx.services.processEntry` | Module-level bootstrap that runs the worker |
| Stop timeout | `jAGFx.services.C_DEFAULT_STOP_TIMEOUT` | Default join budget |
| Task helper | `utilities.createTask` | Schedule the parent receiver |
| Device | `fluxCore.devices.SCRCPY` | Serial, name |
| Options | `SCRCPYOptions` | Optional emitter options |
| Queue helpers | `closeQueue`, `asyncCloseQueue` | Close plus cancel feeder thread |
| Protocol | `iSCRCPYEmitter` / `iEmitter` | Structural contract: service, subscription, device |
| Trace | builtin `trace` | Logging. Installed by `__monkeyPatch`, declared in `typings/__builtins__.pyi`. |

Not used by this base, and not required by the contract: a sentinel value, a second process-lifecycle implementation, or an explicit `iSCRCPYEmitter` base.

---

## 9. Boundaries

In scope:

- Starting and stopping named client processes.
- `_clientWorker`, in its own module, running in each client.
- Bidirectional queue transport.
- Cooperative and forced shutdown.
- Parent-side receiver on the shared inbound queue.
- Device identity inherited from SCRCPY.

Out of scope:

- What a message means.
- How a supplied worker interprets a message.
- UI binding.
- Persistence.
- Broadcasting one message to every client.

---

## 10. Acceptance checks

One script: `.test/smoke/emitters/test_opemitter_message_path.py`. It `trace`s every check and every hop.

1. `start` with no running loop creates nothing. This check runs before `asyncio.run`.
2. Two starts with the same `clientId` — the second fails, the first keeps running.
3. A message put on a client's dedicated outbound queue is received by that client only.
4. A message put by any client on the shared outbound queue is received by the parent's single inbound receiver.
5. `stop` sets the event, every client exits, the parent receiver finishes, every queue is closed, and `ON_STOPPED` fires once.
6. A second `stop` while the first is in flight does not start a second shutdown.
7. A start that fails midway leaves no process and no open queue.
8. `running()` is false after the shutdown event is set, and false when no processes remain. `running(clientId)` is true only while that client's process is alive.
9. `_clientWorker` is a module-level coroutine in its own module. Starting a client on spawn imports that module and does not pickle the emitter.
