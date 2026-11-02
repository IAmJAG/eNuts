# ==================================================================================
from pathlib import Path
from typing import Dict, Optional, Union

# ==================================================================================
import torch

# ==================================================================================
from torch import Tensor, nn
from torch import device as torchDevice
from torchvision.models import (
    MobileNet_V3_Small_Weights,
    MobileNetV3,
    mobilenet_v3_small,
)

# ==================================================================================
from jAGFx.serializer import jsonDecode

# ==================================================================================
from ..types.interface.policy import iPolicy
from ..utilities import getTorchDevice
from .__policyOption import PolicyOptions
from .__utilities import buildBackbone


# ==================================================================================
class DCPolicyCore(iPolicy, nn.Module):
    VERSION: str = "0.0.1"
    def __init__(
        self, module: Optional[nn.Module] = None,         
        device: Optional[str | torchDevice] = "cuda", *args, **kwargs,
    ) -> None:        
        if module is None:
            module: MobileNetV3 = mobilenet_v3_small(
                weights=MobileNet_V3_Small_Weights.DEFAULT
            )
        opts: PolicyOptions = PolicyOptions(module, kwargs)
        self._device: torchDevice = getTorchDevice(device)
        
        super().__init__(*args, **kwargs)

        backbone: nn.Module = buildBackbone(module).to(self.device)
        module.to(self.device)

        if opts.freezeBackbone:
            for param in backbone.parameters():
                param.requires_grad = False
        
        featureDimension: int = opts.featureDimension
        slotInputDim: int = (
            featureDimension
            + opts.intentEmbeddingDimension
            + opts.actionEmbeddingDimension
            + opts.parameterKindEmbeddingDimension,
        )[0]
        
        
        self.slotMerge = nn.Sequential(
            nn.Linear(slotInputDim, featureDimension),
            nn.ReLU(inplace=True),
        ).to(self.device)        

        self.contextMerge = nn.Sequential(
            nn.Linear(featureDimension + opts.intentEmbeddingDimension, featureDimension),
            nn.ReLU(inplace=True),
        ).to(self.device)

        self.actionHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, opts.actionEmbeddingDimension),
        ).to(self.device)

        self.parameterKindHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, opts.parameterKindEmbeddingDimension),
        ).to(self.device)

        self.spatialHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, opts.spatialOutputDimension),
            nn.Sigmoid(),
        ).to(self.device)

        self.backbone: nn.Module = backbone
        self._options: PolicyOptions = opts

    @property
    def options(self) -> PolicyOptions:
        return self._options

# region [INTILLISENSE] retained for intellisense and type hinting purposes    
    def backbone(self, *args, **kwargs) -> Tensor:
        ...
    def slotMerge(self, *args, **kwargs) -> Tensor:
        ...
    def contextMerge(self, *args, **kwargs) -> Tensor:
        ...
    def actionHead(self, *args, **kwargs) -> Tensor:
        ...
    def parameterKindHead(self, *args, **kwargs) -> Tensor:
        ...
    def spatialHead(self, *args, **kwargs) -> Tensor:
        ...
# endregion

    @property
    def device(self) -> torchDevice:
        return self._device

    def forward(
        self,
        intent: Tensor, intentSpace: Tensor,
        visualSpace: Tensor, actionSpace: Tensor, parameterSpace: Tensor,
    ) -> Dict[str, Tensor]:
        device = self.device

        intent = intent.to(device)
        intentSpace = intentSpace.to(device)
        visualSpace = visualSpace.to(device)
        actionSpace = actionSpace.to(device)
        parameterSpace = parameterSpace.to(device)

        # 4D = unbatched [T, C, H, W]; 5D = batched [B, T, C, H, W]
        batched = visualSpace.dim() == 5
        if batched:
            B, T, C, H, W = visualSpace.shape
            visFlat = visualSpace.reshape(B * T, C, H, W)

        else:
            T = visualSpace.shape[0]
            B = 1
            visFlat = visualSpace

        visualFeatures: nn.Module
        if self.options.freezeBackbone:
            with torch.no_grad():
                visualFeatures = self.backbone(visFlat)

        else:
            visualFeatures = self.backbone(visFlat)

        # visualFeatures: [B*T, F] or [T, F]
        if batched:
            F = visualFeatures.shape[-1]
            visualFeatures = visualFeatures.reshape(B, T, F)
            # history tensors already [B, T, D]
        # else: visualFeatures is [T, F]; history is [T, D]

        slotInput = torch.cat(
            [visualFeatures, intentSpace, actionSpace, parameterSpace],
            dim=-1,
        )
        slotVector = self.slotMerge(slotInput)

        # reduce over time only
        timeDim = 1 if batched else 0
        slotMean = slotVector.mean(dim=timeDim)          # [B, F] or [F]

        # intent blanket: make sure last-dim is I and batch matches
        if intent.dim() == 1:
            intent = intent.unsqueeze(0)                 # [1, I]
        if batched and intent.shape[0] == 1 and B > 1:
            intent = intent.expand(B, -1)                # [B, I]

        intentBlanket = torch.cat([slotMean, intent], dim=-1)
        context = self.contextMerge(intentBlanket)       # [B, F] or [1, F]

        return {
            "ACTION": self.actionHead(context),
            "PARAMETERKIND": self.parameterKindHead(context),
            "SPATIAL": self.spatialHead(context),
        }

    def save(self, path: str | Path) -> None: 
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "VERSION": self.VERSION, 
                "MODELSTATE": self.state_dict(),
                "OPTIONS": self.options.encode(),
            }, path
        )
    
    @classmethod
    def load(cls, path: str | Path, module: nn.Module = None, device: Optional[Union[str, torchDevice]] = "cuda",) -> iPolicy:
        model: Dict = torch.load(path, map_location="cpu", weights_only=False)

        version: str = model.get("VERSION", None)
        if not version or version != cls.VERSION:
            raise ValueError(
                f"Unsupported policy checkpoint version: {model.get('VERSION')!r}"
            )
        
        if "MODELSTATE" not in model:
            raise ValueError("Policy checkpoint missing MODELSTATE")

        if "OPTIONS" not in model:
            raise ValueError("Policy checkpoint missing OPTIONS")
        
        options: PolicyOptions = jsonDecode(model["OPTIONS"])
        policy = cls(module, device=device, **options)
        policy.load_state_dict(model["MODELSTATE"], strict=True)
        return policy
