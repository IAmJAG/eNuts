# ==================================================================================
from __future__ import annotations

from typing import Any


# ==================================================================================
class IpcDeviceStream:
    """Deferred cross-process stream. Not implemented for v1."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "IpcDeviceStream deferred; use LocalDeviceStream (in-process SW path)."
        )


__all__ = ["IpcDeviceStream"]