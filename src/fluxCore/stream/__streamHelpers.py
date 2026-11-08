# ==================================================================================
from __future__ import annotations

# ==================================================================================
C_DEFAULT_RING_SIZE: int = 2
C_RING_SIZES: list[int] = [2, 4, 8, 16, 32, 64, 128, 256]
C_MIN_RING_SIZE: int = 2
# ==================================================================================

# ==================================================================================
def validateRingSize(size: int) -> int:
    if size < C_MIN_RING_SIZE: return C_DEFAULT_RING_SIZE
    if size in C_RING_SIZES: return size
    nearestSize = min(C_RING_SIZES, key=lambda val: abs(val - size))
    return nearestSize

# ==================================================================================
__all__ = [
    "C_DEFAULT_RING_SIZE",
    "C_MIN_RING_SIZE",
    "C_RING_SIZES",
    "validateRingSize",
]
# ==================================================================================
