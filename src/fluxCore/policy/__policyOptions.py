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
C_STACK_SIZES: frozenset[int] = frozenset({4, 8, 16, 32, 64})
C_DEFAULT_STACK_SIZE: int = 16
C_DEFAULT_DURATION_SEC: float = 1.0


# ==================================================================================
class PolicyOptions(Serializable):
    """Serializable policy construction options.

    Owns only configuration. Vocabularies and seed data are supplied by the caller
    (application or tests) — not defined here.

    stackSize / durationSec configure StreamingPolicy carousel and time gate.
    Frame representation (ndarray vs tensor) is not an option — handled at push.
    """

    def __init__(
        self,
        actions: Optional[Vocabulary] = None,
        argumentKinds: Optional[Vocabulary] = None,
        featureDim: int = G_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        stackSize: int = C_DEFAULT_STACK_SIZE,
        durationSec: float = C_DEFAULT_DURATION_SEC,
    ) -> None:
        super().__init__()

        self._actions: Optional[Vocabulary] = actions
        self._argumentKinds: Optional[Vocabulary] = argumentKinds
        self._featureDimension: int = int(featureDim)
        self._freezeBackbone: bool = bool(freezeBackbone)
        self._stackSize: int = int(stackSize)
        self._durationSec: float = float(durationSec)

        self._validateStackSize(self._stackSize)
        self._validateDurationSec(self._durationSec)

        self.Properties.extend(
            [
                "actions",
                "argumentKinds",
                "featureDimension",
                "freezeBackbone",
                "stackSize",
                "durationSec",
            ]
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _validateStackSize(value: int) -> None:
        if int(value) not in C_STACK_SIZES:
            raise ValueError(
                f"stackSize must be one of {sorted(C_STACK_SIZES)}, got {value!r}"
            )

    @staticmethod
    def _validateDurationSec(value: float) -> None:
        if float(value) <= 0:
            raise ValueError(f"durationSec must be > 0, got {value!r}")

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

    @property
    def stackSize(self) -> int:
        return self._stackSize

    @stackSize.setter
    def stackSize(self, value: int) -> None:
        self._validateStackSize(value)
        self._stackSize = int(value)

    @property
    def durationSec(self) -> float:
        return self._durationSec

    @durationSec.setter
    def durationSec(self, value: float) -> None:
        self._validateDurationSec(value)
        self._durationSec = float(value)
