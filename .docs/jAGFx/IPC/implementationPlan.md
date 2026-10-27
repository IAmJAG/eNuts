# IPC Implementation Plan

**Status:** Plan only — no Endpoint/Bridge code until phases are executed  
**Branch:** `development`  
**Scope:** Message extensions, `Endpoint`, Bridge registration and correlation  
**Out of scope for this plan:** payload-kind conventions (defer to first concrete Bridge), shared-memory / large binary transport

---

## Phase overview

| Phase | Goal | Deliverable |
|-------|------|-------------|
| **0** | Docs already aligned | Done (`IPC.md`, `requirement.md`, `implementation.md`) |
| **1** | Extend `Message` | `timestamp`, `isTerminal` on interface + implementation |
| **2** | `Endpoint` skeleton | start/stop, async `send`, inbound/outbound tasks, no correlation yet |
| **3** | Bridge contract + registration | `iBridge`, register/unregister, kind → bridge dispatch |
| **4** | Correlation + terminal lifecycle | two-level maps, unmap-then-push / deliver-then-unmap rules |
| **5** | Package exports + docs sync | `__init__` exports, inventory, final doc pass |

Do not start a later phase until the previous phase’s code and its mirrored `.docs` notes are consistent.

After each phase that changes code: run `.scripts/updateInventory.py` before commit (project rule).

---

## Phase 1 — Message envelope

### Goal
Every IPC message carries a chronologically sortable timestamp and a terminal flag.

### Files

| File | Change |
|------|--------|
| `src/jAGFx/types/interface/communication/__message.py` | Add `timestamp` and `isTerminal` to `iMessage` |
| `src/jAGFx/IPC/__message.py` | Implement fields; extend `Properties` for encode/decode |
| `.docs/jAGFx/IPC/implementation.md` | Note Message fields complete |

### Code changes

**`iMessage`**

```python
@property
def timestamp(self) -> float: ...   # or datetime; pick one and stick to it

@property
def isTerminal(self) -> bool: ...
```

**Recommendation:** `float` seconds since epoch (UTC) for simple chronological sort across processes; `Serializable` already supports `datetime` if preferred — choose **one** in Phase 1 and document it.

**`Message.__init__`**

```python
def __init__(
    self,
    payload: iSerializable,
    correlationId: UUID | None = None,
    isTerminal: bool = False,
    timestamp: float | None = None,
) -> None:
    ...
    self._correlationId = correlationId or uuid4()
    self._messageId = uuid4()
    self._isTerminal = isTerminal
    self._timestamp = timestamp if timestamp is not None else time.time()
    self.Properties.extend([
        "payload", "correlationId", "messageId", "timestamp", "isTerminal",
    ])
```

Add public properties `timestamp` and `isTerminal` (read-only is enough unless a setter is required for decode).

### Acceptance

- Round-trip encode/decode preserves `timestamp` and `isTerminal`.
- Default `isTerminal` is `False`; default `timestamp` is “now”.

---

## Phase 2 — Endpoint skeleton

### Goal
Process-local endpoint that owns `IOQueue`, runs inbound/outbound tasks, and exposes `await send(message)` with **no** correlation logic yet (push-only).

### Files

| File | Change |
|------|--------|
| `src/jAGFx/types/interface/communication/__endpoint.py` | **New** — `iEndpoint` protocol |
| `src/jAGFx/types/interface/communication/__init__.py` | Export `iEndpoint` |
| `src/jAGFx/IPC/__endpoint.py` | **New** — `Endpoint` class |
| `src/jAGFx/IPC/__init__.py` | Export `Endpoint` (and keep `IOQueue`) |
| `.docs/jAGFx/IPC/IPC.md` / `implementation.md` | Point at real module paths |

### `iEndpoint` surface (minimal)

```python
class iEndpoint(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def send(self, message: iMessage) -> None: ...
```

### `Endpoint` behavior

```text
__init__(ioQueue: iIOQueue)

start:
  create asyncio.Queue for outbound
  spawn inbound poll task  (to_thread(ioQueue.receive, timeout))
  spawn outbound sender task (async queue → ioQueue.send)

stop:
  signal stopping
  cancel/await tasks with finite grace
  (queue close ownership stays explicit; may be Phase 5 polish)

send(message):
  await outboundQueue.put(message)   # non-blocking enqueue from caller’s perspective after await put
```

Inbound in Phase 2: decode and **log or no-op drop** (no bridge dispatch yet). That keeps the phase testable without Bridge.

### Acceptance

- Two processes with reversed `IOQueue`s can `await send` and the peer’s inbound task observes messages.
- Stop does not hang indefinitely.

---

## Phase 3 — Bridge contract and registration

### Goal
Bridges register handlers; endpoint dispatches **new** conversations by kind; bridges call `await endpoint.send`.

### Files

| File | Change |
|------|--------|
| `src/jAGFx/types/interface/communication/__bridge.py` | **New** — `iBridge` |
| `src/jAGFx/types/interface/communication/__init__.py` | Export `iBridge` |
| `src/jAGFx/IPC/__endpoint.py` | `registerBridge` / `unregisterBridge`; kind map; inbound dispatch |
| `src/jAGFx/IPC/__bridge.py` | **New** — optional thin base `Bridge` implementing attach/detach + handler dict |
| `.docs/jAGFx/IPC/` | Update bridge registration section if wording drifts |

### `iBridge` surface

```python
class iBridge(Protocol):
    @property
    def messageHandlers(self) -> Mapping[str, Callable[..., Awaitable[None] | None]]: ...
    # keys: serializable kind strings (open-ended; defined per concrete bridge later)

    def attachEndpoint(self, endpoint: iEndpoint) -> None: ...
    def detachEndpoint(self) -> None: ...
```

Handler signatures can be refined in implementation; inbound delivery should be awaitable if the handler is a coroutine.

### Endpoint additions

```text
registerBridge(bridge):
  for each kind in bridge.messageHandlers:
    reject if kind already owned
    map kind → bridge
  bridge.attachEndpoint(self)

unregisterBridge(bridge):
  remove kind bindings for that bridge
  bridge.detachEndpoint()

inbound dispatch (no correlation yet):
  resolve kind from message (payload type name or explicit kind field — concrete extraction when first bridge lands)
  bridge = kind map
  invoke handler
```

**Note:** Exact “kind string from message” extraction is intentionally open until the first real Bridge; Phase 3 can use a temporary convention (e.g. payload `__type__` or a small helper) documented as provisional.

### Acceptance

- Register two bridges with disjoint kinds; inbound messages invoke the correct handler.
- Duplicate kind registration fails clearly.
- Bridge can `await endpoint.send(...)` after attach.

---

## Phase 4 — Correlation and terminal lifecycle

### Goal
Two-level maps and locked terminal rules.

### Files

| File | Change |
|------|--------|
| `src/jAGFx/IPC/__endpoint.py` | `correlationId → bridge`; bind/unbind; terminal handling on send/receive |
| `src/jAGFx/IPC/__bridge.py` (or base) | `correlationId → processor`; register/unregister processor |
| `src/jAGFx/types/interface/communication/__bridge.py` | Optional processor methods on `iBridge` |
| `.docs/jAGFx/IPC/IPC.md` | Confirm lifecycle matches code |

### Endpoint rules (locked)

**`await send(message)`**

```text
if message.isTerminal:
    if correlationId in map: drop correlationId → bridge
    notify owning bridge to drop processor if still attached  # or bridge does this before calling send
    then enqueue message
else:
    # registration is bridge-driven before send:
    #   bridge.registerProcessor(id, processor)
    #   endpoint.bindCorrelation(id, bridge)
    enqueue message
```

Prefer: bridge performs its processor register/unregister; endpoint only owns `correlationId → bridge`. On terminal send, endpoint unmaps its entry if present; bridge unmaps processor if present **before or as part of** the send call path—implementation must match docs: unmap then push.

**Inbound**

```text
if correlationId in endpoint map:
    bridge = map[id]
else:
    bridge = kind map
deliver to bridge (processor if present, else kind handler)
if message.isTerminal:
    endpoint unmap if present
    bridge unmap processor if present
```

### Bridge processor API

```text
registerProcessor(correlationId, callable)   # only for non-terminal conversations
unregisterProcessor(correlationId)         # if present
```

No Future-based `request` API on Endpoint in this plan.

### Acceptance

- Non-terminal send leaves maps populated; terminal send clears them and still delivers on the peer.
- Multi-bridge: response with `correlationId` routes to the bridge that bound it.
- Double-terminal or unknown id does not crash (unmap only if present).

---

## Phase 5 — Package surface and cleanup

### Goal
Public imports, interface completeness, docs/inventory.

### Files

| File | Change |
|------|--------|
| `src/jAGFx/IPC/__init__.py` | Export `IOQueue`, `Message`, `Endpoint`, and Bridge base if public |
| `src/jAGFx/types/interface/communication/__init__.py` | Export `iIOQueue`, `iMessage`, `iEndpoint`, `iBridge` |
| `.docs/jAGFx/IPC/implementation.md` | Mark phases 1–4 done; list real paths |
| `.docs/jAGFx/IPC/IPC.md` | Status line → transport + Endpoint/Bridge implemented |
| `.scripts/updateInventory.py` | Run; commit inventory if required |

### Optional polish (same phase or follow-up)

- Explicit queue close ownership helper on Endpoint stop
- Structured logging on orphan messages / unknown kinds
- Unit tests under `.test/` for Message round-trip and Endpoint send/receive (no real domain bridge required)

---

## File change checklist (all phases)

### Existing files to modify

| Path | Phases |
|------|--------|
| `src/jAGFx/IPC/__message.py` | 1 |
| `src/jAGFx/IPC/__init__.py` | 2, 5 |
| `src/jAGFx/types/interface/communication/__message.py` | 1 |
| `src/jAGFx/types/interface/communication/__init__.py` | 2, 3, 5 |
| `.docs/jAGFx/IPC/IPC.md` | 2–5 (status / paths) |
| `.docs/jAGFx/IPC/implementation.md` | 1–5 |
| `.docs/jAGFx/IPC/requirement.md` | only if FR text drifts |

### New files

| Path | Phase |
|------|-------|
| `src/jAGFx/types/interface/communication/__endpoint.py` | 2 |
| `src/jAGFx/types/interface/communication/__bridge.py` | 3 |
| `src/jAGFx/IPC/__endpoint.py` | 2 (extend 3–4) |
| `src/jAGFx/IPC/__bridge.py` | 3 (extend 4) |
| `.docs/jAGFx/IPC/implementationPlan.md` | this document |

### Explicitly not in this plan

| Item | When |
|------|------|
| Payload kind string conventions | First concrete Bridge implementation |
| Shared memory / large binary path | Separate plan when frames or similar are needed |
| Domain bridges (SCRCPY, recorder, etc.) | Application layers after Endpoint is stable |
| `Endpoint.request` / Future helper | Not required; request ⊂ command |

---

## Suggested execution order (practical)

1. Phase 1 (Message) — small, unblocks everything.  
2. Phase 2 (Endpoint push path) — prove two-process async send/receive.  
3. Phase 3 (registration + kind dispatch) — prove multi-bridge routing.  
4. Phase 4 (correlation + terminal) — prove conversation lifecycle.  
5. Phase 5 (exports + inventory + doc status).

Each phase should be one or few commits with matching doc touch-ups under `.docs/jAGFx/IPC/`.
