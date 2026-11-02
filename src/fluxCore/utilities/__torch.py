# ==================================================================================
import hashlib
import json

# ==================================================================================
from typing import Any, Dict, List, Optional, Union

# ==================================================================================
from torch import Generator as TorchGenerator
from torch import Tensor
from torch import device as torchDevice
from torch import float32 as TFloat
from torch import randn as TorchRandn
from torch.cuda import is_available
from torch.nn.functional import normalize as tfNormalize

# ==================================================================================
G_DEFAULT_EMBED_DIM: int = 128
G_DEFAULT_FEATURE_DIM: int = 576

G_NORMALIZE_MEAN: List[float] = [0.485, 0.456, 0.406]
G_NORMALIZE_STD: List[float] = [0.229, 0.224, 0.225]

G_FRAME_SIZE: int = 224
G_PARAM_DIM: int = 8
# ==================================================================================


# ==================================================================================
def getTorchDevice(device: Optional[Union[torchDevice, str]] = None) -> torchDevice:
    if device is None:
        device = "cuda" if is_available() else "cpu"

    if isinstance(device, str):
        if device.lower().startswith("cuda") and not is_available():
            device = "cpu"
        return torchDevice(device)

    return device


# ==================================================================================
def deterministicEmbedding(
    key: str | Dict[str, Any], embedDim: int, device: Optional[str | torchDevice] = None
) -> Tensor:
    device: torchDevice = getTorchDevice(device)

    if isinstance(key, dict):
        serialized = json.dumps(key, sort_keys=True, ensure_ascii=False)
    else:
        serialized = str(key)

    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16) % (2**63 - 1)

    generator = TorchGenerator()
    generator.manual_seed(seed)

    vector = TorchRandn(embedDim, generator=generator, dtype=TFloat).to(device)
    return tfNormalize(vector, p=2, dim=0).to(device)

