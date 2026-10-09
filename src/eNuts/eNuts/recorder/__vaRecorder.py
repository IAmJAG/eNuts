# ==================================================================================
# Video Action Recorder
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import json

# ==================================================================================
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path

# ==================================================================================
from av import Packet
from av import open as openVideo
from av.container import Container
from av.stream import Stream

# ==================================================================================
from fluxCore.types.interface.packets import iFrame

# ==================================================================================
VIDEO_EXTENSION = ".mp4"
ACTION_LOG_EXTENSION = ".jsonl"
# ==================================================================================

# ==================================================================================
class VARecorder:
    def __init__(self, name: str, datasetPath: str | Path, w: int, h: int) -> None:
        videoPath: str | Path = Path(datasetPath) / name / f"{name}.{VIDEO_EXTENSION}"
        actionLogPath: str | Path = Path(datasetPath) / name / f"{name}.{ACTION_LOG_EXTENSION}"

        # Open PyAV container for writing
        container: Container = openVideo(str(videoPath), mode="w")        
        stream: Stream = container.add_stream("h264")
        stream.width = w
        stream.height = h

        actionFile: TextIOWrapper = open(actionLogPath, "w", encoding="utf-8")

        self._container: Container = container
        self._stream: Stream = stream
        self._actionFile: TextIOWrapper = actionFile
        self._isConfigured: bool = False

        self._videoPath: str | Path = Path(videoPath)
        self._actionLogPath: str | Path = Path(actionLogPath)

    def pushFrame(self, frame: iFrame) -> None:
        if frame.isConfig:  
            self._stream.codec_context.extradata = frame.payload
            self._isConfigured = True
            return

        lPacket: Packet = Packet(frame.payload)  
        lPacket.pts = frame.pts 
        lPacket.dts = frame.pts
        lPacket.time_base = Fraction(1, 1_000_000_000)
        lPacket.is_keyframe = frame.isKeyFrame
        lPacket.stream = self._stream

        try:
            self._container.mux(lPacket)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] pushFrame failed", ex)
            self.close()

    def logAction(self, pts: int, intentIndex: int, actionIndex: int) -> None:
        try:
            lRecord = { "pts": pts, "intentIndex": intentIndex, "actionIndex": actionIndex}
            self._actionFile.write(json.dumps(lRecord) + "\n")

        except Exception as ex:
            error(f"[{self.__class__.__name__}] logAction failed", ex)

    def close(self) -> None:
        try: 
            try:
                self._container.close()
            
            finally:
                self._actionFile.close()

        except Exception as ex:
            error(f"[{self.__class__.__name__}] close failed", ex)
