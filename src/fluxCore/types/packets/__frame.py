# ==================================================================================
# src/fluxCore/types/packets/__frame.py
# ==================================================================================
from fractions import Fraction

# ==================================================================================
from av import Packet as AVPacket
from av import VideoCodecContext, VideoFrame
from torch import Tensor, from_dlpack

# ==================================================================================
from ..interface.packets import iFrame
from .__packet import Packet


# ==================================================================================
class Frame(Packet, iFrame):
    def __init__(self, data: bytes, pts: int, isConfig: bool, isKeyFrame: bool):
        super().__init__(data)
        self._isKeyFrame: bool = isKeyFrame
        self._isConfig: bool = isConfig
        self._pts: int = pts

    @property
    def isKeyFrame(self) -> bool:
        return self._isKeyFrame

    @isKeyFrame.setter
    def isKeyFrame(self, value: bool) -> None:
        self._isKeyFrame = value

    @property
    def isConfig(self) -> bool:
        return self._isConfig

    @isConfig.setter
    def isConfig(self, value: bool) -> None:
        self._isConfig = value

    @property
    def pts(self) -> int:
        return self._pts

    @pts.setter
    def pts(self, value: int) -> None:
        self._pts = value

    def decode(
        self, decoder: VideoCodecContext | None = None, toGPU: bool = False
    ) -> VideoFrame | Tensor | None:
        if decoder is None:
            raise ValueError("decode() requires a VideoCodecContext decoder.")

        # SPS/PPS (and similar) are not picture NALs — only feed extradata, do not decode.
        if self.isConfig:
            decoder.extradata = self.payload
            return None

        packet: AVPacket = AVPacket(self._payload)
        packet.pts = self._pts
        packet.time_base = Fraction(1, 1_000_000_000)
        packet.is_keyframe = self._isKeyFrame

        frames: list[VideoFrame] = decoder.decode(packet)
        if not frames:
            return None

        lFrame = frames[0]
        if not toGPU:
            return lFrame

        if not self._isHwFrame(lFrame):
            lFmt = getattr(getattr(lFrame, "format", None), "name", None)
            lHw = getattr(lFrame, "hw_frames_ctx", None)

            raise RuntimeError(
                "decodeToGpu=True but frame is software "
                f"(format={lFmt!r}, hw_frames_ctx={lHw!r}). "
                "NVDEC did not produce a device frame; refusing CPU copy."
            )

        return self._frameToCudaTensor(lFrame)

    @staticmethod
    def _isHwFrame(frame: VideoFrame) -> bool:
        if getattr(frame, "hw_frames_ctx", None) is not None:
            return True

        if frame.planes:
            lPlane0 = frame.planes[0]
            if hasattr(lPlane0, "__dlpack__"):
                try:
                    lPlane0.__dlpack__()
                    return True
                except Exception:
                    return False

        return False

    @staticmethod
    def _frameToCudaTensor(frame: VideoFrame) -> Tensor:
        if frame.planes:
            lPlane0 = frame.planes[0]
            if hasattr(lPlane0, "__dlpack__"):
                lTensor = from_dlpack(lPlane0)
                if not lTensor.is_cuda:
                    raise RuntimeError(
                        "DLPack plane is not on CUDA; refusing host tensor."
                    )
                return lTensor

        if hasattr(frame, "__dlpack__"):
            lTensor = from_dlpack(frame)
            if not lTensor.is_cuda:
                raise RuntimeError(
                    "DLPack frame is not on CUDA; refusing host tensor."
                )

            return lTensor

        raise RuntimeError(
            "HW frame has no DLPack export; cannot form CUDA tensor "
            "without a host copy."
        )
