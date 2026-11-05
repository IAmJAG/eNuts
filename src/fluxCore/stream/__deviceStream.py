# ==================================================================================
from __future__ import annotations

# ==================================================================================
from functools import partial
from typing import List, Tuple

# ==================================================================================
from PySide6.QtGui import QImage

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.emitters import iEmitter
from fluxCore.types.interface.packets import iFrame
from jAGFx.services import AsyncSubscription

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
class LocalDeviceStream(AsyncSubscription):
    EVENTS: List[str] = [
        C_ON_FRAME, C_ON_METADATA_UPDATE, C_ON_ERROR, C_ON_INITIALIZED,
        C_ON_STARTING, C_ON_STARTED, C_ON_STOPPING, C_ON_STOPPED,
        C_ON_PAUSED, C_ON_RESUMED,
    ]
    def __init__(self) -> None:
        super().__init__()
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
            for event in self.EVENTS: 
                callback = partial(self._onEvent, event)
                emitter.subscribe(event, callback)

            self._emitter: iEmitter = emitter   

        except Exception as ex:
            raise ex
        
        finally:
            emitter.setSuppressEvent(False)

    def detachedEmitter(self) -> None:
        emitter: iEmitter = self._emitter

        try:
            if emitter is None: return
            emitter.setSuppressEvent(True)
            decoder: FrameDecoder = self._decoder

            # DIRECT EMITTER EVENTS
            emitter.unsubscribe(C_ON_INITIALIZED, decoder.setCodecContext)
            for event in self.EVENTS:
                callbacks = emitter._callbacks.get(event, [])
                for callback in callbacks:
                    if (
                        isinstance(callback, partial)
                        and callback.func == self._onEvent
                    ):
                        emitter.unsubscribe(event, callback)

        except Exception:
            raise 

        finally:            
            self._emitter = None

    async def stop(self) -> None:
        emitter: iEmitter = self._emitter
        if emitter is None: raise ValueError("No emitter attached")
        emitter.stop()        

    async def start(self) -> None:
        emitter: iEmitter = self._emitter
        if emitter is None: raise ValueError("No emitter attached")
        
        decoder: FrameDecoder = self._decoder
        if decoder is None: raise ValueError("Decoder not set")
        
        if emitter.isRunning: 
            raise RuntimeError("Emitter is already running")        

        try:
            emitter.start()

        except Exception as ex:
            raise ex        

        self._previousSize: Tuple[int, int] = (0, 0)
        emitter.unsubscribe(C_ON_FRAME, self._onFrame)
        emitter.subscribe(C_ON_FRAME, self._onFrame)
        
        serial: str = self._emitter.id
        verbose(f"[{self.classname()}] subscribed ON_FRAME id={serial!r}")

    async def _onFrame(self, frame: iFrame) -> None:        
        try:
            prevSize: Tuple[int, int] = self._previousSize
            decoder: FrameDecoder = self._decoder            

            qimg: QImage = decoder.decode(frame, eDecodeFormat.QIMAGE)
            if qimg is None or qimg.isNull(): return

            newSize: Tuple[int, int] = (qimg.width(), qimg.height())

            flag: FrameFlags = FrameFlags.NONE
            if frame.isKeyFrame: flag |= FrameFlags.KEYFRAME                
            if newSize != prevSize:
                device: iDevice = self._emitter.toDevice(self._emitter)
                self.raiseEvent(C_ON_METADATA_UPDATE, device)                    
                flag |= FrameFlags.RESOLUTION_CHANGED
            
            header: FrameHeader = FrameHeader(
                pts=frame.pts, width=newSize[0], height=newSize[1], 
                format=eDecodeFormat.QIMAGE, flags=flag
            )
            
            self._previousSize = newSize
            self.raiseEvent(C_ON_FRAME, header, qimg)

        except Exception as ex:
            warning(f"[{self.classname()}] _onFrame failed", ex)
            raise ex