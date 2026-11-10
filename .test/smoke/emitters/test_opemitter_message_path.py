# ==================================================================================
"""Parent puts 'ping'. Child echoes. Parent receiver records 'echo:ping'."""
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
    emitter = ProbeEmitter(serial="probe")
    emitter.start()
    try:
        assert emitter.isRunning, "child did not start"
        emitter._outQueue.put("ping")

        for _ in range(100):
            if emitter.received:
                break
            await asyncio.sleep(0.05)

        assert emitter.isRunning, "child died before reply"
        assert emitter.received == ["echo:ping"], emitter.received
    finally:
        await emitter.stopAsync(timeout=2.0)


def test_opemitter_message_roundtrip() -> None:
    asyncio.run(_roundtrip())
