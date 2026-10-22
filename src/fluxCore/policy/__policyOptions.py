# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ..utilities import G_DEFAULT_FEATURE_DIM
from .vocabulary import Vocabulary


# ==================================================================================
class PolicyOptions(Serializable):
    def __init__(
        self,
        actions: Optional[Vocabulary] = None,
        argumentKinds: Optional[Vocabulary] = None,
        featureDim: int = G_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
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
    def actions(self) -> Optional[Vocabulary]:
        return self._actions

    @actions.setter
    def actions(self, value: Optional[Vocabulary]) -> None:
        self._actions = value

    @property
    def argumentKinds(self) -> Optional[Vocabulary]:
        return self._argumentKinds

    @argumentKinds.setter
    def argumentKinds(self, value: Optional[Vocabulary]) -> None:
        self._argumentKinds = value

    @property
    def featureDimension(self) -> int:
        return self._featureDimension

    @featureDimension.setter
    def featureDimension(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("featureDimension must be >= 1")
        self._featureDimension = int(value)

    @property
    def freezeBackbone(self) -> bool:
        return self._freezeBackbone

    @freezeBackbone.setter
    def freezeBackbone(self, value: bool) -> None:
        self._freezeBackbone = bool(value)
