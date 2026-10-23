# ==================================================================================
import hashlib
import json

# ==================================================================================
from typing import Any, Dict, List, Optional, Union

# ==================================================================================
from torch import Generator as TorchGenerator
from torch import Tensor
from torch import device as TorchDevice
from torch import float32 as TFloat
from torch import randn as TorchRandn
from torch.cuda import is_available
from torch.nn.functional import normalize as tfNormalize

# ==================================================================================
G_DEFAULT_EMBED_DIM: int = 128
G_DEFAULT_FEATURE_DIM: int = 576
# MobileNet V3 Small features + AdaptiveAvgPool2d(1) + Flatten
G_BACKBONE_DIM: int = 576

G_NORMALIZE_MEAN: List[float] = [0.485, 0.456, 0.406]
G_NORMALIZE_STD: List[float] = [0.229, 0.224, 0.225]

G_FRAME_SIZE: int = 224
G_PARAM_DIM: int = 8
# ==================================================================================


# ==================================================================================
def getTorchDevice(device: Optional[Union[TorchDevice, str]] = None) -> TorchDevice:
    if device is None:
        device = "cuda" if is_available() else "cpu"

    if isinstance(device, str):
        if device.lower().startswith("cuda") and not is_available():
            device = "cpu"
        return TorchDevice(device)

    return device


# ==================================================================================
def deterministicEmbedding(key: str | Dict[str, Any], embedDim: int) -> Tensor:
    """
    Generates a pseudo-random deterministic embedding tensor from a string or dictionary key.
    Dictionaries are deterministically serialized with sorted keys to ensure stable hashing.
    """
    if isinstance(key, dict):
        lSerialized = json.dumps(key, sort_keys=True, ensure_ascii=False)
    else:
        lSerialized = str(key)

    lDigest = hashlib.sha256(lSerialized.encode("utf-8")).hexdigest()
    lSeed = int(lDigest[:16], 16) % (2**63 - 1)

    lGenerator = TorchGenerator()
    lGenerator.manual_seed(lSeed)

    lVector = TorchRandn(embedDim, generator=lGenerator, dtype=TFloat)
    return tfNormalize(lVector, p=2, dim=0)
