# ==================================================================================
from typing import Any, Dict, List, Optional, Union

# ==================================================================================
from torch import nn
from torchvision import models

# ==================================================================================
G_DEFAULT_EMBEDDING_DIMENSION: int = 128
G_DEFAULT_FREEZE_BACKBONE: bool = True
G_DEFAULT_SPATIAL_OUTPUT_DIMENSION: int = 4

G_NORMALIZE_MEAN: List[float] = [0.485, 0.456, 0.406]
G_NORMALIZE_STD: List[float] = [0.229, 0.224, 0.225]

G_DEFAULT_IMAGE_RESIZE: int = 224
G_PARAM_DIM: int = 8

G_DEFAULT_STACK_SIZE: int = 4

G_DEFAULT_FEATURE_DIMENSION: int = 576
# ==================================================================================

def getFeatureDimension(module: nn.Module) -> int:
    if isinstance(module, models.MobileNetV3):
        return int(module.last_channel)  
    
    if isinstance(module, models.ResNet):
        return int(module.fc.in_features)
    
    raise ValueError(f"Unsupported backbone type: {type(module)!r}")

def buildBackbone(module: nn.Module) -> nn.Module:
    if isinstance(module, models.MobileNetV3):
        return nn.Sequential(
            module.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
    
    if isinstance(module, models.ResNet):
        return nn.Sequential(
            module.conv1,
            module.bn1,
            module.relu,
            module.maxpool,
            module.layer1,
            module.layer2,
            module.layer3,
            module.layer4,
            module.avgpool,
            nn.Flatten(),
        )
    raise ValueError(f"Unsupported backbone: {type(module)!r}")