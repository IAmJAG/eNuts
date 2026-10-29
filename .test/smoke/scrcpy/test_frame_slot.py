# ==================================================================================
"""Smoke: FrameSlotHeader wire layout and ring helpers (no Qt, no ADB)."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
import sys

# ==================================================================================
_REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from fluxCore.emitters.scrcpy import (  # noqa: E402
    C_DEFAULT_RING_SIZE,
    C_FRAME_SLOT_HEADER_SIZE,
    C_FRAME_SLOT_MAGIC,
    FramePresentFormat,
    FrameSlotFlags,
    FrameSlotHeader,
    clampRingSize,
    makeFrameSlotHeader,
    nextRingIndex,
    pickWriteIndex,
    shouldSkipPresent,
)


# ==================================================================================
def test_header_size_is_40() -> None:
    assert C_FRAME_SLOT_HEADER_SIZE == 40


def test_pack_unpack_roundtrip() -> None:
    hdr = makeFrameSlotHeader(
        seq=42,
        pts=1_000_000,
        width=1080,
        height=1920,
        format=FramePresentFormat.RGBA8,
        flags=FrameSlotFlags.KEYFRAME | FrameSlotFlags.RESOLUTION_CHANGED,
    )
    raw = hdr.pack()
    assert len(raw) == C_FRAME_SLOT_HEADER_SIZE
    back = FrameSlotHeader.unpack(raw)
    back.validateMagic()
    assert back.magic == C_FRAME_SLOT_MAGIC
    assert back.seq == 42
    assert back.pts == 1_000_000
    assert back.width == 1080
    assert back.height == 1920
    assert back.stride == 1080 * 4
    assert back.presentFormat is FramePresentFormat.RGBA8
    assert FrameSlotFlags.KEYFRAME in back.slotFlags
    assert FrameSlotFlags.RESOLUTION_CHANGED in back.slotFlags


def test_bad_magic_raises() -> None:
    hdr = makeFrameSlotHeader(seq=1, width=10, height=10)
    raw = bytearray(hdr.pack())
    raw[0] = 0
    bad = FrameSlotHeader.unpack(raw)
    try:
        bad.validateMagic()
        raised = False
    except ValueError:
        raised = True
    assert raised is True


def test_ring_size_clamp() -> None:
    assert clampRingSize(3) == C_DEFAULT_RING_SIZE
    try:
        clampRingSize(1)
        ok = False
    except ValueError:
        ok = True
    assert ok is True


def test_pick_write_avoids_display() -> None:
    for display in range(3):
        w = pickWriteIndex(displayIndex=display, ringSize=3)
        assert w != display
        assert 0 <= w < 3


def test_next_ring_index() -> None:
    assert nextRingIndex(0, 3) == 1
    assert nextRingIndex(2, 3) == 0


def test_should_skip_present() -> None:
    assert shouldSkipPresent(slotSeq=5, lastPresentedSeq=None) is False
    assert shouldSkipPresent(slotSeq=5, lastPresentedSeq=5) is True
    assert shouldSkipPresent(slotSeq=6, lastPresentedSeq=5) is False
