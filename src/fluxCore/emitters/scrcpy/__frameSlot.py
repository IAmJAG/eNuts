# ==================================================================================
"""Frame-plane slot contract (not Message JSON).

Full reconstructed frames after decode. Header is the per-slot truth for present.
GPU handles are opaque and platform-specific; this module only defines meta + ring rules.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import IntEnum, IntFlag, unique
from struct import Struct, error as StructError
from typing import NamedTuple

# ==================================================================================
# Wire layout (little-endian), fixed size — stable across processes.
# magic u32 | seq u64 | pts u64 | w u32 | h u32 | stride u32 | format u32 | flags u32
# ==================================================================================
C_FRAME_SLOT_MAGIC: int = 0x534C4F54  # 'SLOT'
C_FRAME_SLOT_HEADER_STRUCT: Struct = Struct("<IQQIIII I".replace(" ", ""))
# I Q Q I I I I I  → 4+8+8+4+4+4+4+4 = 40 bytes
C_FRAME_SLOT_HEADER_SIZE: int = C_FRAME_SLOT_HEADER_STRUCT.size

C_DEFAULT_RING_SIZE: int = 3
C_MIN_RING_SIZE: int = 2
C_MAX_RING_SIZE: int = 4


# ==================================================================================
@unique
class FramePresentFormat(IntEnum):
    """Agreed at openStream; slot.format must match session (or RESOLUTION_CHANGED)."""

    UNKNOWN = 0
    RGBA8 = 1
    BGRA8 = 2
    RGB8 = 3
    NV12 = 4
    # Platform opaque surfaces (handle carries real layout)
    PLATFORM_OPAQUE = 100


@unique
class FrameSlotFlags(IntFlag):
    NONE = 0
    RESOLUTION_CHANGED = 1 << 0  # hint: w/h/format differ from previous seq
    KEYFRAME = 1 << 1  # full refresh / discontinuity
    EOS = 1 << 2  # end of stream


# ==================================================================================
class FrameSlotHeader(NamedTuple):
    magic: int
    seq: int
    pts: int  # presentation time, microseconds (stream clock); 0 if unknown
    width: int
    height: int
    stride: int
    format: int  # FramePresentFormat value
    flags: int  # FrameSlotFlags bits

    def pack(self) -> bytes:
        return C_FRAME_SLOT_HEADER_STRUCT.pack(
            self.magic,
            self.seq,
            self.pts,
            self.width,
            self.height,
            self.stride,
            self.format,
            self.flags,
        )

    @classmethod
    def unpack(cls, data: bytes | memoryview) -> FrameSlotHeader:
        if len(data) < C_FRAME_SLOT_HEADER_SIZE:
            raise ValueError(
                f"FrameSlotHeader needs {C_FRAME_SLOT_HEADER_SIZE} bytes, got {len(data)}"
            )
        try:
            fields = C_FRAME_SLOT_HEADER_STRUCT.unpack_from(data)
        except StructError as ex:
            raise ValueError("FrameSlotHeader unpack failed") from ex
        return cls(*fields)

    def validateMagic(self) -> None:
        if self.magic != C_FRAME_SLOT_MAGIC:
            raise ValueError(f"bad frame slot magic: 0x{self.magic:08X}")

    @property
    def presentFormat(self) -> FramePresentFormat:
        try:
            return FramePresentFormat(self.format)
        except ValueError:
            return FramePresentFormat.UNKNOWN

    @property
    def slotFlags(self) -> FrameSlotFlags:
        return FrameSlotFlags(self.flags & int(FrameSlotFlags.EOS) * 2 - 1) if False else FrameSlotFlags(self.flags)


def makeFrameSlotHeader(
    *,
    seq: int,
    pts: int = 0,
    width: int,
    height: int,
    stride: int = 0,
    format: FramePresentFormat | int = FramePresentFormat.RGBA8,
    flags: FrameSlotFlags | int = FrameSlotFlags.NONE,
) -> FrameSlotHeader:
    fmt = int(format)
    fl = int(flags)
    if stride <= 0 and width > 0:
        # sensible default for packed 8-bit RGBA/BGRA; callers should set for NV12
        if fmt in (int(FramePresentFormat.RGBA8), int(FramePresentFormat.BGRA8)):
            stride = width * 4
        elif fmt == int(FramePresentFormat.RGB8):
            stride = width * 3
        else:
            stride = width
    return FrameSlotHeader(
        magic=C_FRAME_SLOT_MAGIC,
        seq=int(seq),
        pts=int(pts),
        width=int(width),
        height=int(height),
        stride=int(stride),
        format=fmt,
        flags=fl,
    )


# ==================================================================================
# Ring index helpers (collision-free triple-buffer style)
# ==================================================================================
def clampRingSize(n: int) -> int:
    if n < C_MIN_RING_SIZE or n > C_MAX_RING_SIZE:
        raise ValueError(
            f"ring size must be in [{C_MIN_RING_SIZE}, {C_MAX_RING_SIZE}], got {n}"
        )
    return n

def nextRingIndex(current: int, ringSize: int) -> int:
    ringSize = clampRingSize(ringSize)
    return (int(current) + 1) % ringSize

def pickWriteIndex(*, displayIndex: int, ringSize: int, preferred: int | None = None) -> int:
    """Choose a write slot that is not the one main is displaying."""
    ringSize = clampRingSize(ringSize)
    displayIndex = int(displayIndex) % ringSize
    if preferred is not None:
        p = int(preferred) % ringSize
        if p != displayIndex:
            return p
    # advance from display until a different slot
    idx = nextRingIndex(displayIndex, ringSize)
    return idx


def shouldSkipPresent(*, slotSeq: int, lastPresentedSeq: int | None) -> bool:
    """True if this publish was already presented (same seq)."""
    if lastPresentedSeq is None:
        return False
    return int(slotSeq) == int(lastPresentedSeq)


# ==================================================================================
__all__ = [
    "C_FRAME_SLOT_MAGIC",
    "C_FRAME_SLOT_HEADER_SIZE",
    "C_FRAME_SLOT_HEADER_STRUCT",
    "C_DEFAULT_RING_SIZE",
    "C_MIN_RING_SIZE",
    "C_MAX_RING_SIZE",
    "FramePresentFormat",
    "FrameSlotFlags",
    "FrameSlotHeader",
    "makeFrameSlotHeader",
    "clampRingSize",
    "nextRingIndex",
    "pickWriteIndex",
    "shouldSkipPresent",
]
