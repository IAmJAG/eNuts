# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

# ==================================================================================
from fluxCore.types.interface.emitters import iEmitter
from jAGFx.types.interface.services import iService


# ==================================================================================
@runtime_checkable
class iKGRecorderService(iService, Protocol):
    """Records every encoded frame from an emitter plus key/pointer events."""

    @property
    def isRecording(self) -> bool: ...

    @property
    def sessionId(self) -> Optional[str]: ...

    @property
    def events(self) -> List[Dict[str, Any]]: ...

    @property
    def frameCount(self) -> int: ...

    def bind(
        self,
        emitter: iEmitter,
        *,
        serial: str,
        width: int,
        height: int,
        codec: str = "h264",
    ) -> None: ...

    def start(self, sessionDir: str | Path, *args, **kwargs) -> None: ...
    def stop(self, *args, **kwargs) -> Dict[str, Any]: ...

    def logKey(self, action: str, key: str) -> None: ...
    def logPointer(self, action: str, x: int, y: int) -> None: ...
    def clearEvents(self) -> None: ...


# ==================================================================================
__all__ = ["iKGRecorderService"]
