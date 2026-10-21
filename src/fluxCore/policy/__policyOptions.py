# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ..utilities import G_DEFAULT_EMBED_DIM, G_DEFAULT_FEATURE_DIM
from .vocabulary import Vocabulary

# ==================================================================================
C_SEED_ACTIONS: dict[str, str] = {
    "down": "finger/right mouse button down",
    "up": "finger/right mouse button up",
    "move": "finger/mouse move",
    "inject": "send key or text",
}
C_SEED_ARGUMENT_KINDS: dict[str, str] = {
    "coordinate": "normalized point (x, y)",
    "box": "normalized box (left, top, width, height)",
    "key": "keyboard key code (open-ended value)",
    "text": "text string (open-ended value)",
}
C_DEFAULT_FEATURE_DIM: int = 512


# ==================================================================================
class PolicyOptions(Serializable):
    def __init__(
        self, actions: Optional[Vocabulary], argumentKinds: Optional[Vocabulary],
        featureDim: int = G_DEFAULT_FEATURE_DIM, freezeBackbone: bool = True
    ) -> None:
        super().__init__()

        self._actions: Optional[Vocabulary] = actions
        self._argumentKinds: Optional[Vocabulary] = argumentKinds
        self._featureDimension: int = int(featureDim)

        self._freezeBackbone: bool = bool(freezeBackbone)

        self.Properties.extend(
            [
                "actions",
                "argumentKinds",                
                "featureDimension",
                "freezeBackbone",
            ]
        )

    # ------------------------------------------------------------------
    @property
    def actions(self) -> Vocabulary:
        return self._actions

    @actions.setter
    def actions(self, value: Vocabulary) -> None:
        self._actions = value

    @property
    def argumentKinds(self) -> Vocabulary:
        return self._argumentKinds

    @argumentKinds.setter
    def argumentKinds(self, value: Vocabulary | None) -> None:
        self._argumentKinds = value

    @property
    def featureDimension(self) -> int:
        return self._featureDimension

    @featureDimension.setter
    def featureDimension(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("featureDim must be >= 1")
        
        self._featureDimension = int(value)

    @property
    def freezeBackbone(self) -> bool:
        return self._freezeBackbone

    @freezeBackbone.setter
    def freezeBackbone(self, value: bool) -> None:
        self._freezeBackbone = bool(value)
    