# ==================================================================================
"""outOfProcessEmitter acceptance — message path via module-level echoWorker.

Layout (src/TEST):

    src/TEST/smoke/emitters/outOfProcessEmitter.py   ← this file

Data flow (parent owns every queue):

    parent._outQueues[clientId]  →  that client's inbound  →  echoWorker
    echoWorker                   →  parent._inQueue (shared)  →  parent receiver

Run from repo root:

    set PYTHONPATH=src
    python src/TEST/smoke/emitters/outOfProcessEmitter.py
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
import inspect
import sys
from pathlib import Path
from queue import Empty
from typing import Any, List, Optional

# ==================================================================================
# Allow `python src/TEST/smoke/emitters/outOfProcessEmitter.py` from repo root.
_SRC = Path(__file__).resolve().parents[3]  # .../src
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ==================================================================================
import __monkeyPatch  # noqa: E402, F401 — builtins.trace, setupLogging, createTask

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent

# ==================================================================================
from fluxCore.emitters.__emitterWorkers import echoWorker
from fluxCore.emitters.__outProcessEmitter import outOfProcessEmitter
from jAGFx.logging import TRACE

# ==================================================================================
_FLOW: List[str] = []
_FAILED: List[str] = []
# ==================================================================================


def _check(name: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    line = f"{mark}  {name}" + (f"  {detail}" if detail else "")
    trace(line)
    if not ok:
        _FAILED.append(line)


def _hop(text: str) -> None:
    _FLOW.append(text)
    trace(f"FLOW  {text}")


# ==================================================================================
class _ProbeEmitter(outOfProcessEmitter):
    """outOfProcessEmitter with echoWorker + collected inbound replies."""

    def __init__(self, serial: str = "probe") -> None:
        super().__init__(serial=serial, name=serial, worker=echoWorker)
        self.received: List[Any] = []

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        isShuttingdown = shutdownEvent.is_set
        try:
            while not isShuttingdown():
                try:
                    msg = await to_thread(queue.get, True, 0.1)
                except Empty:
                    continue
                self.received.append(msg)
                trace(f"FLOW  parent inbound got {msg!r}  received={self.received}")
        finally:
            return


# ==================================================================================
async def _wait(emitter: _ProbeEmitter, count: int, timeout: float = 5.0) -> bool:
    steps = max(1, int(timeout / 0.05))
    for _ in range(steps):
        if len(emitter.received) >= count:
            return True
        await asyncio.sleep(0.05)
    return False


def _checkNoLoop() -> None:
    """Must run with no event loop. asyncio.run already has one."""
    cold = _ProbeEmitter(serial="probe-cold")
    try:
        cold.start("a")
        noLoop = False
    except RuntimeError:
        noLoop = True
    _check(
        "start without loop creates nothing",
        noLoop and not cold._processes and cold._inQueue is None,
    )


# ==================================================================================
async def program(*args) -> None:
    trace("---- outOfProcessEmitter acceptance (echoWorker) ----")

    _check(
        "echoWorker module-level coroutine",
        inspect.iscoroutinefunction(echoWorker)
        and inspect.isfunction(echoWorker)
        and echoWorker.__module__ == "fluxCore.emitters.__emitterWorkers",
        f"module={echoWorker.__module__!r}",
    )

    emitter = _ProbeEmitter(serial="probe")
    stopped: List[str] = []
    emitter.subscribe("ON_STOPPING", lambda: stopped.append("ON_STOPPING"))
    emitter.subscribe("ON_STOPPED", lambda: stopped.append("ON_STOPPED"))

    # --- client a -----------------------------------------------------------
    emitter.start("a")
    _hop("start a  -> dedicated outQueues[a], shared inQueue, receiver task")
    _check("running() after start a", emitter.running())
    _check("running(a) after start a", emitter.running("a"))
    _check("running(b) before b exists", not emitter.running("b"))
    _check("outQueues has a", "a" in emitter._outQueues)
    _check("shared inQueue created", emitter._inQueue is not None)

    await emitter._dispatch("a", "ping")
    _hop("parent put(a, 'ping') -> outQueues[a]  (client a inbound)")
    got = await _wait(emitter, 1)
    _hop(
        f"echoWorker a  -> shared inQueue  -> parent receiver  "
        f"received={emitter.received}"
    )
    _check(
        "roundtrip a:ping",
        got and emitter.received == ["FROM a:ping"],
        str(emitter.received),
    )

    # --- client b -----------------------------------------------------------
    emitter.start("b")
    _hop("start b  -> dedicated outQueues[b], same shared inQueue, same receiver")
    _check("running(b) after start b", emitter.running("b"))
    _check("two outQueues", set(emitter._outQueues) == {"a", "b"})

    before = list(emitter.received)
    await emitter._dispatch("a", "only-a")
    _hop("parent put(a, 'only-a') -> outQueues[a] only")
    got = await _wait(emitter, 2)
    _hop(f"after only-a  received={emitter.received}")
    _check(
        "addressed: only a replies",
        got
        and emitter.received == before + ["FROM a:only-a"]
        and not any(str(m).startswith("FROM b:") for m in emitter.received),
        str(emitter.received),
    )

    await emitter._dispatch("b", "only-b")
    _hop("parent put(b, 'only-b') -> outQueues[b] only")
    got = await _wait(emitter, 3)
    _hop(f"after only-b  received={emitter.received}")
    _check(
        "addressed: b replies on same inbound",
        got and emitter.received[-1] == "FROM b:only-b",
        str(emitter.received),
    )

    # --- duplicate client ---------------------------------------------------
    try:
        emitter.start("a")
        duplicate = False
    except RuntimeError:
        duplicate = True
    _check("duplicate client rejected", duplicate and emitter.running("a"))

    # --- stop coalesce ------------------------------------------------------
    emitter.stop()
    emitter.stop()
    _hop("stop + stop  -> one retained stop task")
    await emitter.waitStopped()
    _check(
        "stop coalesced and finished",
        not emitter.running() and not emitter.running("a") and not emitter.running("b"),
    )
    _check(
        "ON_STOPPING then ON_STOPPED",
        stopped == ["ON_STOPPING", "ON_STOPPED"],
        str(stopped),
    )
    _check(
        "queues cleared",
        emitter._inQueue is None and not emitter._outQueues,
    )

    # --- flow summary -------------------------------------------------------
    trace("---- flow ----")
    for step in _FLOW:
        trace(f"  {step}")

    if _FAILED:
        trace(f"---- {len(_FAILED)} FAILED ----")
        for line in _FAILED:
            trace(f"  {line}")
        raise AssertionError("\n".join(_FAILED))

    trace("---- all passed ----")


# ==================================================================================
if __name__ == "__main__":
    # No-loop check must run before asyncio.run (a loop already exists inside).
    setupLogging("outOfProcessEmitter", TRACE)
    _checkNoLoop()
    asyncio.run(program())
