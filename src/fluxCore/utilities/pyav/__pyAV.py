
# ==================================================================================
from av import CodecContext, VideoCodecContext

# ==================================================================================
try:
    from av.codec.hwaccel import HWAccel, hwdevices_available

    C_HAS_HWACCEL = True

except ImportError:
    debug(
        "WARNING: decodeToGpu=True requires a PyAV build with av.codec.hwaccel.HWAccel. "
    )
    HWAccel = None
    hwdevices_available = None
    C_HAS_HWACCEL = False
# ==================================================================================

# ==================================================================================
def createCodecContext(
    codecId: str, GPUID: int = 0, GPUReady: bool = True
) -> VideoCodecContext:
    lCodec = (codecId or "h264").strip().lower() or "h264"

    if not GPUReady:
        return CodecContext.create(lCodec, "r")

    if not C_HAS_HWACCEL:
        raise RuntimeError(
            "decodeToGpu=True requires a PyAV build with av.codec.hwaccel.HWAccel. "
            "Upgrade PyAV or set decodeToGpu=False."
        )

    lDevices = list(hwdevices_available() or [])
    if "cuda" not in lDevices:
        raise RuntimeError(
            f"decodeToGpu=True needs FFmpeg/PyAV CUDA hwaccel; available={lDevices}. "
            "Rebuild FFmpeg with NVDEC/cuvid support or set decodeToGpu=False."
        )

    lHwaccel = HWAccel(
        device_type="cuda",
        device=str(GPUID),
        allow_software_fallback=False,
        is_hw_owned=True,
    )
    lCtx = CodecContext.create(lCodec, "r", hwaccel=lHwaccel)

    try:
        lCtx.options = {"flags": "low_delay"}

    except Exception:
        pass

    return lCtx
