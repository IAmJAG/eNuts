# ==================================================================================
from typing import Dict, Optional

# ==================================================================================
import torch

# ==================================================================================
from torch import Tensor, nn
from torchvision.models import (
    MobileNet_V3_Small_Weights,
    MobileNetV3,
    mobilenet_v3_small,
)

# ==================================================================================
from ..types.interface.policy import iPolicy
from .__policyOption import PolicyOptions
from .__utilities import buildBackbone


# ==================================================================================
class DCPolicy(iPolicy, nn.Module):
    def __init__(self, module: Optional[nn.Module] = None, *args, **kwargs) -> None:        
        super().__init__(*args)

        if module is None:
            module: MobileNetV3 = mobilenet_v3_small(
                weights=MobileNet_V3_Small_Weights.DEFAULT
            )

        opts: PolicyOptions = PolicyOptions(module, **kwargs)

        backbone: nn.Sequential = buildBackbone(module)

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
        )

        self.contextMerge = nn.Sequential(
            nn.Linear(featureDimension + opts.intentEmbeddingDimension, featureDimension),
            nn.ReLU(inplace=True),
        )

        self.actionHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, opts.actionEmbeddingDimension),
        )

        self.parameterKindHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, opts.parameterKindEmbeddingDimension),
        )

        self.spatialHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, 4),
            nn.Sigmoid(),
        )

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

    def forward(
        self, 
        intent: Tensor,
        intentSpace: Tensor,
        visualSpace: Tensor,
        actionSpace: Tensor,
        parameterSpace: Tensor,
    ) -> Dict[str, Tensor]:

        visualFeatures: Tensor
        if self.options.freezeBackbone:
            with torch.no_grad():
                visualFeatures = self.backbone(visualSpace)
        else:
            visualFeatures = self.backbone(visualSpace)

        slotInput = torch.cat(
            [
                visualFeatures,
                intentSpace,
                actionSpace,
                parameterSpace,
            ],
            dim=-1,
        )
        slotVector: Tensor = self.slotMerge(slotInput)
        slotMean: Tensor = slotVector.mean(dim=0, keepdim=True)

        intentBlanket: Tensor = torch.cat(
            [slotMean, intent], dim=-1
        )
        context: Tensor = self.contextMerge(intentBlanket)

        return {
            "ACTION": self.actionHead(context),
            "PARAMETERKIND": self.parameterKindHead(context),
            "SPATIAL": self.spatialHead(context), # PARAMETER VALUES
        }
