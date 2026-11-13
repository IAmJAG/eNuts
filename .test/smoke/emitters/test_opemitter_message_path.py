# ==================================================================================
"""One run. Every acceptance check. Message path is recorded via trace.

trace is the logging builtin installed by src/__monkeyPatch.py
(setattr(builtins, "trace", trace) from jAGFx.logging) and declared in
typings/__builtins__.pyi. It is not print.

    parent put(client) -> that client's inbound -> echo -> shared inbound -> parent
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
import inspect
from pathlib import Path
import sys

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
_REPO_SRC = _TEST_ROOT.parent / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

import __monkeyPatch  # noqa: E402, F401  — installs builtins.trace
from fixtures.emitters.echoWorker import echoWorker  # noqa: E402
from fixtures.emitters.probe import ProbeEmitter  # noqa: E402
from fluxCore.emitters.__clientWorker import _clientWorker  # noqa: E402


# ==================================================================================
_FLOW: list[str] = []
_FAILED: list[str] = []


def _check(name: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    line = f"{mark}  {name}" + (f"  {detail}" if detail else "")
    trace(line)
    if not ok:
        _FAILED.append(line)


def _hop(text: str) -> None:
    _FLOW.append(text)
    trace(f"FLOW  {text}")


async def _wait(emitter: ProbeEmitter, count: int) -> bool:
    for _ in range(100):
        if len(emitter.received) >= count:
            return True
        await asyncio.sleep(0.05)
    return False


def _checkNoLoop() -> None:
    """Must run with no event loop. asyncio.run already has one."""
    cold = ProbeEmitter(serial="probe")
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
async def run() -> None:
    trace("---- outOfProcessEmitter acceptance ----")

    # 1. Worker is module-level, in its own module.
    _check(
        "worker module-level",
        inspect.iscoroutinefunction(_clientWorker)
        and _clientWorker.__module__ == "fluxCore.emitters.__clientWorker",
        _clientWorker.__module__,
    )
    _check(
        "echo worker module-level",
        inspect.iscoroutinefunction(echoWorker)
        and echoWorker.__module__ == "fixtures.emitters.echoWorker",
        echoWorker.__module__,
    )

    # 2. Start with no loop creates nothing. Done before this coroutine.

    # 3–8. One live emitter. Message path is recorded as it happens.
    emitter = ProbeEmitter(serial="probe")
    stopped: list[str] = []
    emitter.subscribe("ON_STOPPING", lambda: stopped.append("ON_STOPPING"))
    emitter.subscribe("ON_STOPPED", lambda: stopped.append("ON_STOPPED"))

    emitter.start("a")
    _hop("start a  -> dedicated out[a], shared in, receiver")
    _check("running() after start a", emitter.running())
    _check("running(a) after start a", emitter.running("a"))
    _check("running(b) before b exists", not emitter.running("b"))

    await emitter._dispatch("a", "ping")
    _hop("parent put(a, ping) -> out[a]")
    got = await _wait(emitter, 1)
    _hop(f"a echo -> shared in -> parent  received={emitter.received}")
    _check("roundtrip a:ping", got and emitter.received == ["a:ping"], str(emitter.received))

    emitter.start("b")
    _hop("start b  -> dedicated out[b], same shared in, same receiver")
    _check("running(b) after start b", emitter.running("b"))

    before = list(emitter.received)
    await emitter._dispatch("a", "only-a")
    _hop("parent put(a, only-a) -> out[a] only")
    got = await _wait(emitter, 2)
    _hop(f"after only-a  received={emitter.received}")
    _check(
        "addressed: only a replies",
        got and emitter.received == before + ["a:only-a"] and not any(m.startswith("b:") for m in emitter.received),
        str(emitter.received),
    )

    await emitter._dispatch("b", "only-b")
    _hop("parent put(b, only-b) -> out[b] only")
    got = await _wait(emitter, 3)
    _hop(f"after only-b  received={emitter.received}")
    _check("addressed: b replies on same inbound", got and emitter.received[-1] == "b:only-b", str(emitter.received))

    try:
        emitter.start("a")
        duplicate = False
    except RuntimeError:
        duplicate = True
    _check("duplicate client rejected", duplicate and emitter.running("a"))

    # Coalesce: second stop while the first is in flight does nothing extra.
    emitter.stop()
    emitter.stop()
    _hop("stop + stop  -> one retained task")
    await emitter.waitStopped()
    _check("stop coalesced and finished", not emitter.running() and not emitter.running("a"))
    _check("ON_STOPPING then ON_STOPPED", stopped == ["ON_STOPPING", "ON_STOPPED"], str(stopped))
    _check("queues cleared", emitter._inQueue is None and not emitter._outQueues)

    trace("---- flow ----")
    for step in _FLOW:
        trace(f"  {step}")

    if _FAILED:
        trace(f"---- {len(_FAILED)} FAILED ----")
        raise AssertionError("\n".join(_FAILED))

    trace("---- all passed ----")


def test_all() -> None:
    setupLogging("outOfProcessEmitter")
    _checkNoLoop()
    asyncio.run(run())


if __name__ == "__main__":
    setupLogging("outOfProcessEmitter")
    _checkNoLoop()
    asyncio.run(run())
