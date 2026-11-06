# ==================================================================================
from __future__ import annotations

# ==================================================================================
from datetime import datetime, timezone
from json import dump as jsonDump
from pathlib import Path
from time import monotonic
from typing import Any, BinaryIO, Dict, List, Optional
from uuid import uuid4

# ==================================================================================
from fluxCore.types.interface.emitters import iEmitter
from fluxCore.types.interface.packets import iFrame
from jAGFx.services import AsyncService

# ==================================================================================
from ...types.interface.services.recorder import iKGRecorderService

# ==================================================================================
C_ON_FRAME: str = "ON_FRAME"
C_ON_SESSION_STARTED: str = "ON_SESSION_STARTED"
C_ON_SESSION_STOPPED: str = "ON_SESSION_STOPPED"
C_ON_ERROR: str = "ON_ERROR"

C_VIDEO_NAME: str = "video.h264"
C_MANIFEST_NAME: str = "session.json"
C_MANIFEST_VERSION: int = 1
# ==================================================================================


# ==================================================================================
class KGRecorderService(AsyncService):  # structural: iKGRecorderService
    """Capture every emitter ON_FRAME packet + key/pointer events for one session.

    Video is the raw encoded elementary stream (scrcpy/h264 payloads as they
    arrive). Display path (LocalDeviceStream ring) is not used — no skip.
    Events are a single JSON array inside the session manifest. No pause.
    """

    def __init__(self, name: str | None = None) -> None:
        AsyncService.__init__(self, work=self.work, name=name or "KGRecorderService")
        self._emitter: Optional[iEmitter] = None
        self._serial: Optional[str] = None
        self._width: int = 0
        self._height: int = 0
        self._codec: str = "h264"

        self._sessionId: Optional[str] = None
        self._sessionDir: Optional[Path] = None
        self._videoPath: Optional[Path] = None
        self._manifestPath: Optional[Path] = None
        self._videoFile: Optional[BinaryIO] = None

        self._recording: bool = False
        self._sessionStartMono: Optional[float] = None
        self._startedAtUtc: Optional[str] = None
        self._frameCount: int = 0
        self._events: List[Dict[str, Any]] = []
        self._frameSubscribed: bool = False

    # -------------------------------------------------------------------------
    # properties
    # -------------------------------------------------------------------------
    @property
    def isRecording(self) -> bool:
        return self._recording

    @property
    def sessionId(self) -> Optional[str]:
        return self._sessionId

    @property
    def events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    @property
    def frameCount(self) -> int:
        return self._frameCount

    # -------------------------------------------------------------------------
    # bind / session control
    # -------------------------------------------------------------------------
    def bind(
        self,
        emitter: iEmitter,
        *,
        serial: str,
        width: int,
        height: int,
        codec: str = "h264",
    ) -> None:
        if self._recording:
            raise RuntimeError(
                f"[{self.name}] cannot bind while recording sessionId={self._sessionId!r}"
            )
        if emitter is None:
            raise ValueError("emitter is required")
        cleaned = (serial or "").strip()
        if not cleaned:
            raise ValueError("serial is required")

        self._detachFrame()
        self._emitter = emitter
        self._serial = cleaned
        self._width = int(width) if width else 0
        self._height = int(height) if height else 0
        self._codec = (codec or "h264").strip() or "h264"
        verbose(
            f"[{self.name}] bind serial={cleaned!r} "
            f"{self._width}x{self._height} codec={self._codec!r}"
        )

    def start(self, sessionDir: str | Path = None, *args, **kwargs) -> None:
        if self._recording:
            raise RuntimeError(
                f"[{self.name}] already recording sessionId={self._sessionId!r}"
            )
        if self._emitter is None or not self._serial:
            raise RuntimeError(f"[{self.name}] start requires bind(emitter, serial=...)")

        if sessionDir is None:
            raise ValueError("sessionDir is required")

        target = Path(sessionDir)
        target.mkdir(parents=True, exist_ok=True)

        sessionId = target.name or uuid4().hex
        videoPath = target / C_VIDEO_NAME
        manifestPath = target / C_MANIFEST_NAME

        try:
            videoFile = open(videoPath, "wb")
        except OSError as ex:
            error(f"[{self.name}] open video failed path={videoPath}: {ex}")
            raise

        self._sessionId = sessionId
        self._sessionDir = target
        self._videoPath = videoPath
        self._manifestPath = manifestPath
        self._videoFile = videoFile
        self._frameCount = 0
        self._events = []
        self._sessionStartMono = monotonic()
        self._startedAtUtc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._recording = True

        self._attachFrame()

        # AsyncService start: light work loop for wake/stop integration only.
        # Call concrete base explicitly — Protocol must not sit ahead of AsyncService in MRO.
        try:
            if not self.isRunning:
                AsyncService.start(self, *args, **kwargs)
        except RuntimeError:
            # Already running is acceptable if reused across sessions after stop.
            pass

        self.raiseEvent(
            C_ON_SESSION_STARTED,
            {
                "sessionId": sessionId,
                "sessionDir": str(target),
                "videoPath": str(videoPath),
                "serial": self._serial,
            },
        )
        verbose(
            f"[{self.name}] session started id={sessionId!r} dir={str(target)!r}"
        )

    def stop(self, *args, **kwargs) -> Dict[str, Any]:
        if not self._recording:
            return self._emptyResult()

        duration = 0.0
        if self._sessionStartMono is not None:
            duration = max(0.0, monotonic() - self._sessionStartMono)

        self._recording = False
        self._detachFrame()
        self._closeVideoFile()

        result = self._writeManifest(durationSec=duration)

        # Stop AsyncService loop if it was started by us.
        try:
            if self.isRunning:
                AsyncService.stop(self, *args, **kwargs)
        except TypeError:
            # forceAfter-only signature if caller passed unexpected kwargs
            try:
                if self.isRunning:
                    AsyncService.stop(self)
            except RuntimeError as ex:
                warning(f"[{self.name}] AsyncService.stop: {ex}")
        except RuntimeError as ex:
            warning(f"[{self.name}] AsyncService.stop: {ex}")

        self.raiseEvent(C_ON_SESSION_STOPPED, result)
        verbose(
            f"[{self.name}] session stopped id={self._sessionId!r} "
            f"frames={self._frameCount} events={len(self._events)} "
            f"duration={duration:.3f}s"
        )

        self._sessionStartMono = None
        return result

    # -------------------------------------------------------------------------
    # events log
    # -------------------------------------------------------------------------
    def logKey(self, action: str, key: str) -> None:
        if not self._recording:
            return
        self._events.append(
            {
                "t": self._relativeTs(),
                "kind": "key",
                "action": str(action),
                "key": str(key),
            }
        )

    def logPointer(self, action: str, x: int, y: int) -> None:
        if not self._recording:
            return
        self._events.append(
            {
                "t": self._relativeTs(),
                "kind": "pointer",
                "action": str(action),
                "x": int(x),
                "y": int(y),
            }
        )

    def clearEvents(self) -> None:
        self._events.clear()
        if self._recording and self._sessionStartMono is not None:
            self._sessionStartMono = monotonic()
        verbose(f"[{self.name}] events cleared")

    # -------------------------------------------------------------------------
    # AsyncService work (heartbeat only — frames arrive via ON_FRAME)
    # -------------------------------------------------------------------------
    async def work(self, *args, **kwargs) -> None:
        # Capture is event-driven on emitter ON_FRAME. Work is a no-op tick so
        # AsyncService lifecycle (start/stop) remains available to callers.
        return None

    # -------------------------------------------------------------------------
    # frame path — every packet, no ring / no skip
    # -------------------------------------------------------------------------
    def _attachFrame(self) -> None:
        emitter = self._emitter
        if emitter is None or self._frameSubscribed:
            return
        emitter.subscribe(C_ON_FRAME, self._onFrame)
        self._frameSubscribed = True

    def _detachFrame(self) -> None:
        emitter = self._emitter
        if emitter is None or not self._frameSubscribed:
            self._frameSubscribed = False
            return
        try:
            emitter.unsubscribe(C_ON_FRAME, self._onFrame)
        except Exception as ex:
            warning(f"[{self.name}] unsubscribe ON_FRAME failed: {ex}")
        self._frameSubscribed = False

    def _onFrame(self, frame: iFrame, *args, **kwargs) -> None:
        if not self._recording:
            return
        videoFile = self._videoFile
        if videoFile is None:
            return
        try:
            payload = getattr(frame, "payload", None)
            if payload is None:
                payload = getattr(frame, "data", b"")
            if not payload:
                return
            videoFile.write(payload)
            self._frameCount += 1
        except Exception as ex:
            error(f"[{self.name}] write frame failed: {ex}")
            self.raiseEvent(C_ON_ERROR, ex)

    # -------------------------------------------------------------------------
    # helpers
    # -------------------------------------------------------------------------
    def _relativeTs(self) -> float:
        if self._sessionStartMono is None:
            return 0.0
        return max(0.0, monotonic() - self._sessionStartMono)

    def _closeVideoFile(self) -> None:
        videoFile = self._videoFile
        self._videoFile = None
        if videoFile is None:
            return
        try:
            videoFile.flush()
            videoFile.close()
        except Exception as ex:
            warning(f"[{self.name}] close video failed: {ex}")

    def _writeManifest(self, durationSec: float) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "version": C_MANIFEST_VERSION,
            "sessionId": self._sessionId,
            "serial": self._serial,
            "width": self._width,
            "height": self._height,
            "codec": self._codec,
            "startedAt": self._startedAtUtc,
            "durationSec": round(durationSec, 6),
            "frameCount": self._frameCount,
            "video": C_VIDEO_NAME,
            "events": list(self._events),
        }
        manifestPath = self._manifestPath
        if manifestPath is not None:
            try:
                with open(manifestPath, "w", encoding="utf-8") as handle:
                    jsonDump(result, handle, indent=2)
                result["manifestPath"] = str(manifestPath)
            except Exception as ex:
                error(f"[{self.name}] write manifest failed: {ex}")
                self.raiseEvent(C_ON_ERROR, ex)
        if self._videoPath is not None:
            result["videoPath"] = str(self._videoPath)
        if self._sessionDir is not None:
            result["sessionDir"] = str(self._sessionDir)
        return result

    def _emptyResult(self) -> Dict[str, Any]:
        return {
            "version": C_MANIFEST_VERSION,
            "sessionId": self._sessionId,
            "serial": self._serial,
            "width": self._width,
            "height": self._height,
            "codec": self._codec,
            "startedAt": self._startedAtUtc,
            "durationSec": 0.0,
            "frameCount": self._frameCount,
            "video": C_VIDEO_NAME,
            "events": list(self._events),
        }


# ==================================================================================
__all__ = [
    "KGRecorderService",
    "C_ON_SESSION_STARTED",
    "C_ON_SESSION_STOPPED",
    "C_ON_ERROR",
    "C_VIDEO_NAME",
    "C_MANIFEST_NAME",
]
