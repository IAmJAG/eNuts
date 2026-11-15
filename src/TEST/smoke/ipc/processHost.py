# ==================================================================================
"""ProcessHost acceptance — message path via module-level echoWorker.

Entry (same pattern as eNuts apps):

    py .\\src\\main.py --module TEST --app smoke.ipc.processHost

main.py does import_module("TEST.smoke.ipc.processHost") then
calls program(args). Logging is already configured by main.

Data flow (parent owns every queue):

    parent._outQueues[clientId]  →  that client's inbound  →  echoWorker
    echoWorker                   →  parent._inQueue (shared)  →  parent receiver
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
import inspect

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Any, List

# ==================================================================================
from jAGFx.IPC import ProcessHost, echoWorker

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
class _ProbeHost(ProcessHost):
    """ProcessHost with echoWorker + collected inbound replies."""

    def __init__(self, name: str = "probe") -> None:
        super().__init__(name=name, worker=echoWorker)
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
async def _wait(host: _ProbeHost, count: int, timeout: float = 5.0) -> bool:
    steps = max(1, int(timeout / 0.05))
    for _ in range(steps):
        if len(host.received) >= count:
            return True
        await asyncio.sleep(0.05)
    return False


def _checkNoLoop() -> None:
    """Must run with no event loop. asyncio.run already has one."""
    cold = _ProbeHost(name="probe-cold")
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
async def _program() -> None:
    trace("---- ProcessHost acceptance (echoWorker) ----")

    _check(
        "module-level coroutine: echoWorker",
        inspect.iscoroutinefunction(echoWorker) and inspect.isfunction(echoWorker),
        f"module: {echoWorker.__module__!r}",
    )

    host = _ProbeHost(name="probe")
    stopped: List[str] = []
    host.subscribe("ON_STOPPING", lambda: stopped.append("ON_STOPPING"))
    host.subscribe("ON_STOPPED", lambda: stopped.append("ON_STOPPED"))

    # --- client a -----------------------------------------------------------
    host.start("a")
    _hop("start a  -> dedicated outQueues[a], shared inQueue, receiver task")
    _check("running() after start a", host.running())
    _check("running(a) after start a", host.running("a"))
    _check("running(b) before b exists", not host.running("b"))
    _check("outQueues has a", "a" in host._outQueues)
    _check("shared inQueue created", host._inQueue is not None)

    await host._dispatch("a", "ping")
    _hop("parent put(a, 'ping') -> outQueues[a]  (client a inbound)")
    got = await _wait(host, 1)
    _hop(
        f"echoWorker a  -> shared inQueue  -> parent receiver  "
        f"received={host.received}"
    )
    _check(
        "roundtrip a:ping",
        got and host.received == ["FROM a:ping"],
        str(host.received),
    )

    # --- client b -----------------------------------------------------------
    host.start("b")
    _hop("start b  -> dedicated outQueues[b], same shared inQueue, same receiver")
    _check("running(b) after start b", host.running("b"))
    _check("two outQueues", set(host._outQueues) == {"a", "b"})

    before = list(host.received)
    await host._dispatch("a", "only-a")
    _hop("parent put(a, 'only-a') -> outQueues[a] only")
    got = await _wait(host, 2)
    _hop(f"after only-a  received={host.received}")
    _check(
        "addressed: only a replies",
        got
        and host.received == before + ["FROM a:only-a"]
        and not any(str(m).startswith("FROM b:") for m in host.received),
        str(host.received),
    )

    await host._dispatch("b", "only-b")
    _hop("parent put(b, 'only-b') -> outQueues[b] only")
    got = await _wait(host, 3)
    _hop(f"after only-b  received={host.received}")
    _check(
        "addressed: b replies on same inbound",
        got and host.received[-1] == "FROM b:only-b",
        str(host.received),
    )

    # --- duplicate client ---------------------------------------------------
    try:
        host.start("a")
        duplicate = False
    except RuntimeError:
        duplicate = True
    _check("duplicate client rejected", duplicate and host.running("a"))

    # --- stop coalesce ------------------------------------------------------
    host.stop()
    host.stop()
    _hop("stop + stop  -> one retained stop task")
    await host.waitStopped()
    _check(
        "stop coalesced and finished",
        not host.running() and not host.running("a") and not host.running("b"),
    )
    _check(
        "ON_STOPPING then ON_STOPPED",
        stopped == ["ON_STOPPING", "ON_STOPPED"],
        str(stopped),
    )
    _check(
        "queues cleared",
        host._inQueue is None and not host._outQueues,
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
async def _run(*args):
    try:
        await _program()
        return 0
    except AssertionError:
        return 1


# ==================================================================================
def program(*args):
    """
    Entry for main.py: --module TEST --app smoke.ipc.processHost.

    main already called setupLogging. No-loop check must run before asyncio.run.
    """
    try:
        _checkNoLoop()
        asyncio.run(_run(*args))
        return 0
    except AssertionError:
        return 1


# ==================================================================================
if __name__ == "__main__":
    # Direct script run still works when PYTHONPATH includes src.
    raise SystemExit(program())
