# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from torch import device as TorchDevice
from torch.cuda import is_available


# ==================================================================================
def getTorchDevice(device: Optional[Union[TorchDevice, str]]) -> Optional[TorchDevice]:
    if isinstance(device, str):
        isCUDAAvailable: bool = is_available()
        if device.lower().startswith("cuda") and not isCUDAAvailable:
            device = "cpu"
        return TorchDevice(device)
    
    return device
