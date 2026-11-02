# ==================================================================================
from __future__ import annotations

from collections import deque

# ==================================================================================
from typing import List, Optional

# ==================================================================================
from PIL import Image
from torch import Tensor, nn
from torch import device as torchDevice
from torch import stack as torchStack
from torchvision import transforms

# ==================================================================================
from .__dcPolicyCore import DCPolicyCore
from .__policyOption import PolicyOptions


# ==================================================================================
class DCPolicy(DCPolicyCore):
    def __init__(
        self, module: Optional[nn.Module] = None,
        device: Optional[str | torchDevice] = "GPU",
        stackSize: Optional[int] = 4,
        
        *args, **kwargs,
    ) -> None:
        super().__init__(module, device, *args, **kwargs)

        opts: PolicyOptions = self.options        
        self.transform = transforms.Compose(
            [
                transforms.Resize((opts.frameSize, opts.frameSize)),
                transforms.ToTensor(),
                transforms.Normalize(mean=opts.normalizeMean, std=opts.normalizeStd),
            ]
        )

        self._frames: deque[Tensor] = deque[Tensor](maxlen=stackSize)
        self._actions: deque[Tensor] = deque[Tensor](maxlen=stackSize)
        self._parameters: deque[Tensor] = deque[Tensor](maxlen=stackSize)
        self._intents: deque[Tensor] = deque[Tensor](maxlen=stackSize)

# region [INTILLISENSE] retained for intellisense and type hinting purposes    
    def transform(self, x: Tensor) -> Tensor:
        ...
# endregion

    def forward(
        self, activeIntent: Tensor, previousIntent: Tensor,
        image: Image.Image, 
        previousAction: Tensor, previousParameters: Tensor
    ) -> Tensor:        
        activeVisualSpace: Tensor =  self.transform(image).to(self.device)

        self._intents.append(previousIntent)
        self._frames.append(activeVisualSpace)
        self._actions.append(previousAction)
        self._parameters.append(previousParameters)

        intentSpace: Tensor = torchStack(self._intents, dim=0)
        visualSpace: Tensor = torchStack(self._frames, dim=0)
        actionSpace: Tensor = torchStack(self._actions, dim=0)
        parameterSpace: Tensor = torchStack(self._parameters, dim=0)

        return super().forward(activeIntent, intentSpace, visualSpace, actionSpace, parameterSpace) 
