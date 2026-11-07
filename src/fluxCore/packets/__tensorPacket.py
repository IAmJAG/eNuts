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
    def decode(self, decoder: VideoCodecContext, size: int = -1) -> Tensor | None: 
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
        cudaTensor: Tensor
        if self._isHwFrame(vFrame):
            cudaTensor = self._frameToCudaTensor(vFrame)

        else:
            cudaTensor =  self._cpuFrameToCudaTensor(vFrame)

        if size != -1:
            batch = cudaTensor.permute(2, 0, 1).unsqueeze(0).float()            
            lOriginalHeight, lOriginalWidth = batch.shape[2], batch.shape[3]            
            if lOriginalWidth > lOriginalHeight:
                newWidth = size
                newHeight = int(lOriginalHeight * (size / lOriginalWidth))
                
            else:
                newHeight = size
                newWidth = int(lOriginalWidth * (size / lOriginalHeight))

            self.width = newWidth
            self.height = newHeight

            resized = F.interpolate(batch, size=(newHeight, newWidth), mode='bilinear', align_corners=False)
            cudaTensor = resized.squeeze(0).permute(1, 2, 0)

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