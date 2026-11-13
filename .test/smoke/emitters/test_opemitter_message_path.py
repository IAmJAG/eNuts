# ==================================================================================
"""Acceptance checks for outOfProcessEmitter."""
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

from fixtures.emitters.echoWorker import echoWorker  # noqa: E402
from fixtures.emitters.probe import ProbeEmitter  # noqa: E402
from fluxCore.emitters.__clientWorker import _clientWorker  # noqa: E402


# ==================================================================================
async def _waitFor(emitter: ProbeEmitter, count: int) -> None:
    for _ in range(100):
        if len(emitter.received) >= count:
            return
        await asyncio.sleep(0.05)


async def _roundtrip() -> None:
    emitter = ProbeEmitter(serial="probe")
    emitter.start("a")
    try:
        assert emitter.running()
        assert emitter.running("a")
        await emitter._dispatch("a", "ping")
        await _waitFor(emitter, 1)
        assert emitter.received == ["a:ping"], emitter.received
    finally:
        await emitter.stopAsync(timeout=2.0)
        assert not emitter.running()


async def _addressed() -> None:
    emitter = ProbeEmitter(serial="probe")
    emitter.start("a")
    emitter.start("b")
    try:
        await emitter._dispatch("a", "only-a")
        await _waitFor(emitter, 1)
        assert emitter.received == ["a:only-a"], emitter.received
        assert emitter.running("b")
    finally:
        await emitter.stopAsync(timeout=2.0)


async def _duplicate() -> None:
    emitter = ProbeEmitter(serial="probe")
    emitter.start("a")
    try:
        try:
            emitter.start("a")
            raised = False
        except RuntimeError:
            raised = True
        assert raised
        assert emitter.running("a")
    finally:
        await emitter.stopAsync(timeout=2.0)


def test_worker_is_module_level() -> None:
    assert inspect.iscoroutinefunction(_clientWorker)
    assert _clientWorker.__module__ == "fluxCore.emitters.__clientWorker"
    assert inspect.iscoroutinefunction(echoWorker)
    assert echoWorker.__module__ == "fixtures.emitters.echoWorker"


def test_start_without_loop_creates_nothing() -> None:
    emitter = ProbeEmitter(serial="probe")
    try:
        emitter.start("a")
        raised = False
    except RuntimeError:
        raised = True
    assert raised
    assert emitter._processes == {}
    assert emitter._inQueue is None


def test_message_roundtrip() -> None:
    asyncio.run(_roundtrip())


def test_addressed_delivery() -> None:
    asyncio.run(_addressed())


def test_duplicate_client_rejected() -> None:
    asyncio.run(_duplicate())
