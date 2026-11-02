# ==================================================================================
from typing import Any, Dict, List, Optional, Union

# ==================================================================================
from .__utilities import (
    G_DEFAULT_EMBEDDING_DIMENSION,
    G_DEFAULT_FEATURE_DIMENSION,
    G_DEFAULT_FREEZE_BACKBONE,
)


# ==================================================================================
class PolicyOptions:
    DEFAULTS: Dict[str, Any] = {
        "freezeBackbone": G_DEFAULT_FREEZE_BACKBONE,        
        "visualFeatureDimension": G_DEFAULT_FEATURE_DIMENSION,
        "intentEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
        "actionEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
        "parameterKindEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
        "spatialEmbeddingDimension": G_DEFAULT_EMBEDDING_DIMENSION,
    }
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", self.DEFAULTS.get(key, value))
            else:
                warning(f"Unknown option '{key}' provided. Ignoring it.")

    @property
    def freezeBackbone(self) -> bool:
        return self._freezeBackbone

    @freezeBackbone.setter
    def freezeBackbone(self, value: bool) -> None:
        self._freezeBackbone = value

    @property
    def visualFeatureDimension(self) -> int:
        return self._visualFeatureDimension

    @visualFeatureDimension.setter
    def visualFeatureDimension(self, value: int) -> None:
        self._visualFeatureDimension = value

    @property
    def actionEmbeddingDimension(self) -> int:
        return self._actionEmbeddingDimension

    @actionEmbeddingDimension.setter
    def actionEmbeddingDimension(self, value: int) -> None:
        self._actionEmbeddingDimension = value

    @property
    def parameterKindEmbeddingDimension(self) -> int:
        return self._parameterKindEmbeddingDimension

    @parameterKindEmbeddingDimension.setter
    def parameterKindEmbeddingDimension(self, value: int) -> None:
        self._parameterKindEmbeddingDimension = value

    @property
    def spatialEmbeddingDimension(self) -> int:
        return self._spatialEmbeddingDimension

    @spatialEmbeddingDimension.setter
    def spatialEmbeddingDimension(self, value: int) -> None:
        self._spatialEmbeddingDimension = value

    @property
    def intentEmbeddingDimension(self) -> int:
        return self._intentEmbeddingDimension

    @intentEmbeddingDimension.setter
    def intentEmbeddingDimension(self, value: int) -> None:
        self._intentEmbeddingDimension = value