# ==================================================================================
from typing import Any, Dict, List, Optional, Union

# ==================================================================================
from torch import nn
from torchvision import models

# ==================================================================================
from .__utilities import (
    G_DEFAULT_EMBEDDING_DIMENSION,
    G_DEFAULT_FEATURE_DIMENSION,
    G_DEFAULT_FREEZE_BACKBONE,
    G_FEATURE_DIMENSIONS,
    getFeatureDimension,
)


# ==================================================================================
class PolicyOptions:
    DEFAULTS: Dict[str, Any] = {
        "freezeBackbone": G_DEFAULT_FREEZE_BACKBONE,        
        "featureDimension": G_DEFAULT_FEATURE_DIMENSION,
        "intentEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
        "actionEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
        "parameterKindEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
        "spatialEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
    }
    def __init__(self, module: nn.Module, *args, **kwargs) -> None:
        # Set the feature dimension based on the module type
        if isinstance(module, (models.MobileNetV3, models.ResNet)):
            self.DEFAULTS["featureDimension"] = getFeatureDimension(module)

        else:
            raise ValueError(f"Module type {type(module)} not supported.")

        for key, value in kwargs.items():            
            if not hasattr(self, key) or not isinstance(getattr(self, key), property):
                warning(f"Unknown option '{key}' provided. Ignoring it.")
                continue

            defaultValue: Optional[Any] = self.DEFAULTS.get(key, None)
            if defaultValue is None:
                raise ValueError(f"Option '{key}' default value not provided.")

            setattr(self, f"_{key}", self.DEFAULTS.get(key, value))            

    @property
    def freezeBackbone(self) -> bool:
        if not hasattr(self, "_freezeBackbone"):
            self._freezeBackbone = self.DEFAULTS.get("freezeBackbone", G_DEFAULT_FREEZE_BACKBONE)

        return self._freezeBackbone

    @freezeBackbone.setter
    def freezeBackbone(self, value: bool) -> None:
        self._freezeBackbone = value

    @property
    def featureDimension(self) -> int:
        if not hasattr(self, "_featureDimension"):
            self._featureDimension = self.DEFAULTS.get("featureDimension", G_DEFAULT_FEATURE_DIMENSION)

        return self._featureDimension

    @featureDimension.setter
    def featureDimension(self, value: int) -> None:
        self._featureDimension = value

    @property
    def actionEmbeddingDimension(self) -> int:
        if not hasattr(self, "_actionEmbeddingDimension"):
            self._actionEmbeddingDimension = self.DEFAULTS.get("actionEmbeddingDimension", G_DEFAULT_EMBEDDING_DIMENSION)
        return self._actionEmbeddingDimension

    @actionEmbeddingDimension.setter
    def actionEmbeddingDimension(self, value: int) -> None:
        self._actionEmbeddingDimension = value

    @property
    def parameterKindEmbeddingDimension(self) -> int:
        if not hasattr(self, "_parameterKindEmbeddingDimension"):
            self._parameterKindEmbeddingDimension = self.DEFAULTS.get("parameterKindEmbeddingDimension", G_DEFAULT_EMBEDDING_DIMENSION)
        return self._parameterKindEmbeddingDimension

    @parameterKindEmbeddingDimension.setter
    def parameterKindEmbeddingDimension(self, value: int) -> None:
        self._parameterKindEmbeddingDimension = value

    @property
    def spatialEmbeddingDimension(self) -> int:
        if not hasattr(self, "_spatialEmbeddingDimension"):
            self._spatialEmbeddingDimension = self.DEFAULTS.get("spatialEmbeddingDimension", G_DEFAULT_EMBEDDING_DIMENSION)
        return self._spatialEmbeddingDimension

    @spatialEmbeddingDimension.setter
    def spatialEmbeddingDimension(self, value: int) -> None:
        self._spatialEmbeddingDimension = value

    @property
    def intentEmbeddingDimension(self) -> int:
        if not hasattr(self, "_intentEmbeddingDimension"):
            self._intentEmbeddingDimension = self.DEFAULTS.get("intentEmbeddingDimension", G_DEFAULT_EMBEDDING_DIMENSION)
        return self._intentEmbeddingDimension

    @intentEmbeddingDimension.setter
    def intentEmbeddingDimension(self, value: int) -> None:
        self._intentEmbeddingDimension = value
