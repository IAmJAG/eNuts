# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
import sys

# ==================================================================================
_REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from fluxCore.emitters.scrcpy import FrameRing  # noqa: E402


# ==================================================================================
def test_publish_advances_seq() -> None:
    ring = FrameRing(3)
    h1 = ring.publish(width=10, height=20, pts=100)
    h2 = ring.publish(width=10, height=20, pts=200)
    assert h2.seq == h1.seq + 1
    latest = ring.latest()
    assert latest is not None
    assert latest[0].seq == h2.seq


def test_write_avoids_display_slot() -> None:
    ring = FrameRing(3)
    ring.setDisplayIndex(1)
    for _ in range(6):
        ring.publish(width=1, height=1)
        acq = ring.acquireForDisplay()
        assert acq is not None
        idx, hdr, _ = acq
        assert 0 <= idx < 3
