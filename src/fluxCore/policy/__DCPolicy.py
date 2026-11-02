# ==================================================================================
from typing import Optional

from PIL import Image

# ==================================================================================
from torch import Tensor, nn
from torch import device as torchDevice
from torchvision import transforms

# ==================================================================================
from .__dcPolicyCore import DCPolicyCore
from .__policyOption import PolicyOptions


# ==================================================================================
class DCPolicy(DCPolicyCore):
    def __init__(
        self, module: Optional[nn.Module] = None,
        device: Optional[str | torchDevice] = "GPU",
        *args, **kwargs,
    ) -> None:
        super().__init__(module, device, *args, **kwargs)
        s

        opts: PolicyOptions = self.options        
        self.transform = transforms.Compose(
            [
                transforms.Resize((opts.frameSize, opts.frameSize)),
                transforms.ToTensor(),
                transforms.Normalize(mean=opts.normalizeMean, std=opts.normalizeStd),
            ]
        )

# region [INTILLISENSE] retained for intellisense and type hinting purposes    
    def transform(self, x: Tensor) -> Tensor:
        ...
# endregion

    def forward(self, activeIntent: str, image: Image.Image, previousAction: str, previousParameters: str) -> Tensor:
        visualSpace =  self.transform(image).to(self.device).unsqueeze(0)
