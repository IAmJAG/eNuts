# ==================================================================================
"""Smoke: OPEmitter message path, end to end, with trace hops.

Queue wiring (parent perspective):

    parent._outQueue  ==  child inQueue     parent → child
    parent._inQueue   ==  child outQueue    child  → parent

Hops logged with trace():

    1. PARENT send     put on parent._outQueue
    2. CHILD  receive  _receiver pulls from child inQueue
    3. CHILD  reply    put on child outQueue
    4. PARENT receive  _receiver pulls from parent._inQueue
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio
from pathlib import Path
import sys

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
_REPO_SRC = _TEST_ROOT.parent / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

import __monkeyPatch  # noqa: E402, F401  — installs trace as a builtin
from jAGFx.logging import setupLogging  # noqa: E402
from fixtures.emitters.probe import ProbeEmitter  # noqa: E402


# ==================================================================================
async def _roundtrip() -> None:
    setupLogging("opemitter-parent")
    emitter = ProbeEmitter()

    emitter.start()
    try:
        emitter.sendToChild("ping")

        # Parent receiver is polled; give the child time to echo.
        for _ in range(50):
            if emitter.received:
                break
            await asyncWait(0.05)

        assert emitter.received == ["echo:ping"], emitter.received
        trace(f"[PARENT] roundtrip ok: {emitter.received}")

    finally:
        await emitter.stopAsync(timeout=2.0)
        trace("[PARENT] stopped")


def test_opemitter_message_roundtrip() -> None:
    asyncio.run(_roundtrip())
