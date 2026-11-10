# ==================================================================================
"""Parent sends 'ping'. Child echoes 'echo:ping'. Parent receives it."""
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

from fixtures.emitters.probe import ProbeEmitter  # noqa: E402


# ==================================================================================
async def _roundtrip() -> None:
    emitter = ProbeEmitter()
    emitter.start()
    try:
        emitter.send("ping")
        for _ in range(50):
            if emitter.received:
                break
            await asyncWait(0.05)
        assert emitter.received == ["echo:ping"]
    finally:
        await emitter.stopAsync(timeout=2.0)


def test_opemitter_message_roundtrip() -> None:
    asyncio.run(_roundtrip())
