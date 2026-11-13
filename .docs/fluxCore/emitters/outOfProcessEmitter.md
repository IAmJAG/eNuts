# outOfProcessEmitter — Requirements, Rules, and Mental Model

Out-of-process emitter base. Heavy work runs in one or more child processes. The parent (normally the UI event loop) stays responsive.

This document states the contract. It does not prescribe how to implement it.

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

The protocol is structural because the three interface orders cannot be linearized together: `SCRCPY` contributes `iDevice` early, `AsyncProcess` contributes `iSubscription` before `iService`, and `iEmitter` wants `iService`, then `iSubscription`, then `iDevice`.

---

## 3. Mental model

One parent. Many clients. Two directions of traffic. The parent owns every queue.

- **Parent → client.** One outbound queue per client. That queue is the client's inbound. The parent writes to a specific client. Clients do not compete.
- **Client → parent.** One inbound queue on the parent. That queue is the clients' single shared outbound. Every client writes to it. The parent has one receiver on it.
- **Shutdown.** One shared event. Setting it tells every client and the parent receiver to stop.
- **Work.** The only code that runs in a client. One module-level coroutine, given that client's queues.

A client is identified by `clientId`. Starting the same id twice is an error. Starting the first client creates the parent's shared inbound queue and the shared shutdown event. Each start creates that client's dedicated outbound queue. Later clients reuse the shared inbound queue and the event.

Message travel:

```text
parent put(clientId) ──► that client's inbound queue ──► that client only
any client put       ──► parent's single inbound queue ──► parent receiver
```

Ownership, named from the parent:

| Queue | Parent sees it as | Client sees it as | Cardinality |
|-------|-------------------|-------------------|-------------|
| Per-client | outbound to that client | its inbound | one per client |
| Shared | the inbound | its outbound | one for all clients |

---

## 4. Requirements

### 4.1 Startup

- `start(clientId)` requires a running event loop. If there is none, it fails before any process or queue is created.
- A `clientId` that is already started is rejected.
- The first successful start creates the parent's shared inbound queue and the shared shutdown event.
- Each start creates one child process and one dedicated outbound queue for that client.
- The parent has one receiver on the shared inbound queue. It is started with the first client and serves every client.
- Child processes are daemons.
- Work is a module-level coroutine. A bound method is not acceptable, because spawn must import the target by name and must not pickle the emitter.
- If start fails after resources were created, those resources are released. A failed start does not leave an orphaned process or an open queue. If the failure leaves zero clients, the shared inbound queue and the shutdown event are released too.

### 4.2 Messaging

- The parent sends to a client by putting on that client's dedicated outbound queue.
- A client receives only from its own inbound queue. It does not see another client's traffic.
- A client sends to the parent by putting on the shared outbound queue.
- The parent receives every client's messages on its single inbound receiver.
- Payloads are opaque. The base work observes the message. A subclass replaces the observation.
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
  3. Finish the parent receiver (it exits because the event is set).
  4. Join each child. If `forced`, terminate first. If still alive after the timeout, terminate, then kill.
  5. Close every queue and clear client state.
  6. Raise `ON_STOPPED`.
- Cleanup runs even if a step fails. An already-exited process handle is still reaped. "Never started" and "already exited" are different states.
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

## 5. Work — rule and policy

Work is the heavy method. It is the only code that runs inside a client process. Everything else stays on the parent.

### Rule

- Work is a module-level coroutine. It is not a bound method and it is not a nested function.
- Spawn must be able to import it by name. A bound method would pickle the emitter, including its other process handles. That is forbidden.
- Work receives the shutdown event, that client's inbound queue, and the shared outbound queue. It does not receive the parent, and it does not reach into parent state.
- Work watches the shutdown event and exits when it is set. It does not decide process lifetime.
- Work reads only its inbound queue and writes only the shared outbound queue.
- Blocking waits inside work stay in the child. They never touch the parent loop.

### Policy

- The base work observes a message and does nothing else. Meaning belongs to a subclass, which replaces the observation, not the transport.
- Work is the same function for every client. Per-client state is the queues it is given, not a different function.
- On exit, work releases its own queue handles. The parent still owns and closes the queues it created.
- A failing work does not skip handle release. The process may die; the parent still reaps it.

---

## 6. Rules

| Rule | Meaning |
|------|---------|
| Loop before side effects | No process, queue, or task is created until a running loop is confirmed. |
| One owner per client id | A second `start` for the same id fails. |
| Shared in, private out | Parent→client is dedicated per client. Client→parent is one shared queue. |
| Spawn-safe work | Work is a module-level coroutine. Not a bound method. Not a nested function. |
| Cooperative first | Shutdown is signaled by the event. Force is an explicit option. |
| No early close | Queues stay open until the parent receiver has finished and processes have been joined. |
| No leaked handle | Every started process is joined or killed, then closed. Every created queue is closed. |
| Coalesced stop | A stop already in flight is not started again. |
| Observable stop failure | A failure in the scheduled stop is reported, not swallowed. |
| Structural protocol | `iSCRCPYEmitter` is satisfied by shape, not by inheritance. |
| Parent stays on the loop | Blocking queue waits run off the event loop. |

---

## 7. Policies

**Work policy.** Work is the child. It is one module-level coroutine, shared by every client, given that client's inbound queue and the shared outbound queue. It observes the shutdown event and exits. It does not own the process, the event, or the parent's queues. The base observes messages; a subclass replaces that observation.

**Process policy.** Children are daemons. They exit when the parent exits. They are still explicitly joined on stop so handles and feeder threads are released.

**Failure policy.** A failed start rolls back only what that start created. Shared resources are dropped only when the last client is gone.

**Timeout policy.** Stop waits up to the default stop timeout, then escalates to terminate, then to kill. The kill join is short.

**Message policy.** The base emitter does not interpret payloads. It transports them. Interpretation belongs to a subclass.

**Concurrency policy.** The parent receiver is an asyncio task on the parent's loop. Work is an asyncio coroutine inside the child process. The two sides share only queues and the shutdown event.

---

## 8. Available technology

| Layer | What is available | Role |
|-------|-------------------|------|
| Language runtime | Python `asyncio` | Parent loop, child loop, tasks, `to_thread` |
| Process | `multiprocessing.Process` | Child process |
| Signal | `multiprocessing.Event` | Shared shutdown |
| Transport | `multiprocessing.Queue` | Cross-process messages |
| Empty signal | `queue.Empty` | Non-blocking and timed gets |
| Process base | `jAGFx.services.AsyncProcess` | Process lifecycle, name, running, events |
| Spawn entry | `jAGFx.services.processEntry` | Module-level child bootstrap for work |
| Stop timeout | `jAGFx.services.C_DEFAULT_STOP_TIMEOUT` | Default join budget |
| Task helper | `utilities.createTask` | Schedule the parent receiver |
| Device | `fluxCore.devices.SCRCPY` | Serial, name, codec, size |
| Options | `SCRCPYOptions` | Optional emitter options |
| Queue helpers | `closeQueue`, `asyncCloseQueue` | Close plus cancel feeder thread |
| Protocol | `iSCRCPYEmitter` / `iEmitter` | Structural contract: service, subscription, device |

Not used by this base, and not required by the contract: a sentinel value, a second process-lifecycle implementation, or an explicit `iSCRCPYEmitter` base.

---

## 9. Boundaries

In scope:

- Starting and stopping named client processes.
- The work coroutine that runs in each client.
- Bidirectional queue transport.
- Cooperative and forced shutdown.
- Parent-side receiver on the shared inbound queue.
- Device identity inherited from SCRCPY.

Out of scope:

- What a message means.
- How a subclass replaces the observation inside work.
- UI binding.
- Persistence.
- Broadcasting one message to every client.

---

## 10. Acceptance checks

A correct outOfProcessEmitter meets all of these:

1. `start` with no running loop creates nothing.
2. Two starts with the same `clientId` — the second fails, the first keeps running.
3. A message put on a client's dedicated outbound queue is received by that client only.
4. A message put by any client on the shared outbound queue is received by the parent's single inbound receiver.
5. `stop` sets the event, every client exits, the parent receiver finishes, every queue is closed, and `ON_STOPPED` fires once.
6. A second `stop` while the first is in flight does not start a second shutdown.
7. A start that fails midway leaves no process and no open queue.
8. `running()` is false after the shutdown event is set, and false when no processes remain. `running(clientId)` is true only while that client's process is alive.
9. Work is a module-level coroutine. Starting a client on spawn does not pickle the emitter.
