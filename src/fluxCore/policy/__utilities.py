# ==================================================================================
from typing import Any, Dict, List, Optional, Union

# ==================================================================================
from torchvision import models

# ==================================================================================
G_DEFAULT_EMBEDDING_DIMENSION: int = 128
G_DEFAULT_FREEZE_BACKBONE: bool = True

G_NORMALIZE_MEAN: List[float] = [0.485, 0.456, 0.406]
G_NORMALIZE_STD: List[float] = [0.229, 0.224, 0.225]

G_FRAME_SIZE: int = 224
G_PARAM_DIM: int = 8

G_DEFAULT_FEATURE_DIMENSION: int = 576
G_FEATURE_DIMENSIONS: Dict[type, int] = {
    models.mobilenet_v3_small: 576,
    models.mobilenet_v3_large: 960,
    models.resnet18: 512,
    models.resnet34: 512,
    models.resnet50: 2048,
    models.resnet101: 2048,
    models.resnet152: 2048,
}
# ==================================================================================
