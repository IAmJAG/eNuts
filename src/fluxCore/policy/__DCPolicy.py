# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from typing import Dict, List, Optional

# ==================================================================================
from PIL import Image
from torch import Tensor, nn
from torch import cat as torchCat
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
        device: Optional[str | torchDevice] = "cuda",
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

    def _stack(self, buf: deque) -> Tensor:
        items = list(buf)
        maxLen: int = buf.maxlen

        stacked = torchStack(items, dim=0)
        t = stacked.shape[0]        
        if t >= maxLen: return stacked

        pad = stacked.new_zeros((maxLen - t, *stacked.shape[1:]))
        return torchCat([pad, stacked], dim=0)

    def forward(
        self, activeIntent: Tensor, previousIntent: Tensor,
        image: Image.Image, 
        previousAction: Tensor, previousParameters: Tensor
    ) -> Dict[str, Tensor]:        
        device: torchDevice = self.device

        activeVisualSpace: Tensor =  self.transform(image).to(device)
        self._intents.append(previousIntent.to(device))
        self._frames.append(activeVisualSpace.to(device))
        self._actions.append(previousAction.to(device))
        self._parameters.append(previousParameters.to(device))

        intentSpace: Tensor = self._stack(self._intents)
        visualSpace: Tensor = self._stack(self._frames)
        actionSpace: Tensor = self._stack(self._actions)
        parameterSpace: Tensor = self._stack(self._parameters)

        return super().forward(activeIntent, intentSpace, visualSpace, actionSpace, parameterSpace) 
