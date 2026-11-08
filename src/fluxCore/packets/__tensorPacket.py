# ==================================================================================
from fractions import Fraction

# ==================================================================================
from typing import List

# ==================================================================================
from av import Packet as AVPacket
from av import VideoCodecContext, VideoFrame
from torch import Tensor, from_dlpack, from_numpy
from torch.functional import F

# ==================================================================================
from ..types.interface.packets import iImagePacket
from .__SCRCPYPacket import SCRCPYPacket


# ==================================================================================
class TensorPacket(SCRCPYPacket, iImagePacket[Tensor]):
    def decode(self, decoder: VideoCodecContext) -> Tensor | None: 
        if decoder is None:
            raise RuntimeError("decoder is is required.")

        if not hasattr(decoder, "hwaccel"): 
            raise RuntimeError("Decoder is not a HW decoder.")

        payload: bytes = self.payload
        if self.isConfig:
            decoder.extradata = payload
            return None

        packet: AVPacket = AVPacket(payload)
        packet.pts = self._pts
        packet.time_base = Fraction(1, 1_000_000_000)
        packet.is_keyframe = self._isKeyFrame

        vFrames: List[VideoFrame] = decoder.decode(packet)
        if not vFrames or len(vFrames) == 0: return None
        if len(vFrames) > 1:
            raise RuntimeError("decode() decoded more than one frame.")

        vFrame: VideoFrame = vFrames[0]
        self.width = vFrame.width
        self.height = vFrame.height

        cudaTensor: Tensor
        if self._isHwFrame(vFrame):
            cudaTensor = self._frameToCudaTensor(vFrame)

        else:
            cudaTensor =  self._cpuFrameToCudaTensor(vFrame)
        
        return cudaTensor

    @staticmethod
    @staticmethod
    def _isHwFrame(frame: VideoFrame) -> bool:
        if not frame.planes:
            return False

        lPlane0 = frame.planes[0]

        if hasattr(lPlane0, "__dlpack_device__"):
            try:
                lDeviceType, _ = lPlane0.__dlpack_device__()
                return lDeviceType == 2  # kDLCUDA

            except Exception:
                return False

        return getattr(frame, "hw_frames_ctx", None) is not None

    @staticmethod
    def _cpuFrameToCudaTensor(frame: VideoFrame) -> Tensor:
        lRgbFrame = frame.reformat(format="rgb24")
        lNpArray = lRgbFrame.to_ndarray()
        lTensor = from_numpy(lNpArray).to("cuda", non_blocking=True)
        return lTensor

    @staticmethod
    def _frameToCudaTensor(frame: VideoFrame) -> Tensor:
        # Check individual planes first (common for hardware frames like YUV NV12)
        if frame.planes:
            lPlane0 = frame.planes[0]
            if hasattr(lPlane0, "__dlpack__"):
                lTensor = from_dlpack(lPlane0)
                if not lTensor.is_cuda:
                    raise RuntimeError("DLPack plane is not on CUDA; refusing host tensor.")
                return lTensor

        # Fallback to checking the frame itself
        if hasattr(frame, "__dlpack__"):
            lTensor = from_dlpack(frame)
            if not lTensor.is_cuda:
                raise RuntimeError("DLPack frame is not on CUDA; refusing host tensor.")
            return lTensor

        raise RuntimeError(
            "HW frame has no DLPack export; cannot form CUDA tensor without a host copy."
        )