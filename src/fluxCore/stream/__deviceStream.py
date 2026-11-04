# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic
from typing import Any, List, Tuple
from uuid import UUID

# ==================================================================================
from PySide6.QtGui import QImage

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.emitters import iEmitter
from fluxCore.types.interface.packets import iFrame
from jAGFx.services import AsyncService

# ==================================================================================
from .__eDecodeFormat import eDecodeFormat
from .__frameDecoder import FrameDecoder
from .__frameFlags import FrameFlags
from .__frameHeader import FrameHeader

# ==================================================================================
C_ON_FRAME: str = "ON_FRAME"
C_ON_METADATA_UPDATE: str = "ON_METADATA_UPDATE"
C_ON_ERROR: str = "ON_ERROR"
C_ON_INITIALIZED: str = "ON_INITIALIZED"

C_ON_STARTING: str = "ON_STARTING" 
C_ON_STARTED: str = "ON_STARTED"
C_ON_STOPPING: str = "ON_STOPPING"
C_ON_STOPPED: str = "ON_STOPPED"
C_ON_PAUSED: str = "ON_PAUSED"
C_ON_RESUMED: str = "ON_RESUMED"
# ==================================================================================

# ==================================================================================
class LocalDeviceStream(AsyncService):
    EVENTS: List[str] = [
        C_ON_FRAME, C_ON_METADATA_UPDATE, C_ON_ERROR, C_ON_INITIALIZED,
        C_ON_STARTING, C_ON_STARTED, C_ON_STOPPING, C_ON_STOPPED,
        C_ON_PAUSED, C_ON_RESUMED,
    ]
    def __init__(self, ident: str | UUID) -> None:
        self._identity: str | UUID = ident
        self._decoder = FrameDecoder()
        self._emitter: iEmitter = None

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    async def _onEvent(self, event: str, *args, **kwargs) -> None:        
        self.raiseEvent(event, *args, **kwargs)

    def attachedEmitter(self, emitter: iEmitter) -> None:
        emitter: iEmitter = emitter

        try:
            emitter.setSuppressEvent(True)
            decoder: FrameDecoder = self._decoder

            # DIRECT EMITTER EVENTS
            emitter.subscribe(C_ON_INITIALIZED, decoder.setCodecContext)            
            for event in self.EVENTS: emitter.subscribe(event, self._onEvent)

            self._emitter: iEmitter = emitter   

        except Exception as ex:
            raise ex
        
        finally:
            emitter.setSuppressEvent(False)

    def detachedEmitter(self) -> None:
        emitter: iEmitter = self._emitter

        try:
            emitter.setSuppressEvent(True)
            decoder: FrameDecoder = self._decoder

            # DIRECT EMITTER EVENTS
            emitter.unsubscribe(C_ON_INITIALIZED, decoder.setCodecContext)
            for event in self.EVENTS: emitter.unsubscribe(event, self._onEvent)

            self._emitter = None

        except Exception:
            raise 

        finally:
            emitter.setSuppressEvent(False)
            self._emitter = None

    async def stop(self) -> None:
        emitter: iEmitter = self._emitter
        if emitter is None:
            raise ValueError("No emitter attached")

        emitter.stop()

    async def start(self) -> None:
        emitter: iEmitter = self._emitter
        if emitter is None: 
            raise ValueError("No emitter attached")
        
        decoder: FrameDecoder = self._decoder
        if decoder is None:
            raise ValueError("Decoder not set")
        
        if emitter.isRunning: 
            raise RuntimeError("Emitter is already running")        

        try:
            emitter.start()

        except Exception as ex:
            raise ex

        prevSize: Tuple[int, int] = (0, 0)
        sequence: int = None

        async def _onFrame(frame: iFrame) -> None:
            nonlocal prevSize, sequence
            try:
                if frame.isConfig: return

                qimg: QImage = decoder.decode(frame, eDecodeFormat.QIMAGE)
                if qimg is None or qimg.isNull(): return

                sequence = monotonic()
                newSize: Tuple[int, int] = (qimg.width(), qimg.height())

                flag: FrameFlags = FrameFlags.NONE

                if frame.isKeyFrame: flag |= FrameFlags.KEYFRAME                
                if newSize != prevSize:
                    device: iDevice = self._emitter.toDevice(self._emitter)
                    self.raiseEvent(C_ON_METADATA_UPDATE, device)                    
                    flag |= FrameFlags.RESOLUTION_CHANGED
                
                header: FrameHeader = FrameHeader(
                    sequence, frame.pts, *newSize, eDecodeFormat.QIMAGE, flag
                )

                prevSize = newSize
                self.raiseEvent(C_ON_FRAME, header, qimg)

            except Exception as ex:
                warning(f"[{self.classname()}] _onFrame failed", ex)
                raise ex

        self.subscribe(C_ON_FRAME, _onFrame)
        serial: str = self._emitter.id
        verbose(f"[{self.classname()}] subscribed ON_FRAME id={serial!r}")
