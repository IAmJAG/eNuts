# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ..utilities import G_DEFAULT_FEATURE_DIM
from .vocabulary import (
    ActionVocabulary,
    ArgumentKindVocabulary,
    IntentVocabulary,
)

# ==================================================================================
C_STACK_SIZES: frozenset[int] = frozenset({4, 8, 16, 32, 64})
C_DEFAULT_STACK_SIZE: int = 16
C_DEFAULT_DURATION_SEC: float = 1.0
# ==================================================================================
C_NONE_ACTION: str = "NONE"
C_NONE_ARGUMENT_KIND: str = "none"
# ==================================================================================


# ==================================================================================
class PolicyOptions(Serializable):
    def __init__(
        self,
        actions: Optional[ActionVocabulary] = None,
        argumentKinds: Optional[ArgumentKindVocabulary] = None,
        intents: Optional[IntentVocabulary] = None,
        featureDim: int = G_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        stackSize: int = C_DEFAULT_STACK_SIZE,
        durationSec: float = C_DEFAULT_DURATION_SEC,
    ) -> None:
        super().__init__()

        self._actions: Optional[ActionVocabulary] = actions
        self._argumentKinds: Optional[ArgumentKindVocabulary] = argumentKinds
        self._intents: Optional[IntentVocabulary] = intents
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
                "intents",
                "featureDimension",
                "freezeBackbone",
                "stackSize",
                "durationSec",
            ]
        )

    # ------------------------------------------------------------------
    @property
    def acceptIntervalSec(self) -> float:
        """Minimum seconds between accepted carousel slots."""
        return self._durationSec / float(self._stackSize)

    def validate(self) -> None:
        """Require non-empty actions, argumentKinds, and intents."""
        if self._actions is None:
            raise ValueError("PolicyOptions.actions vocabulary is required")
        if self._argumentKinds is None:
            raise ValueError("PolicyOptions.argumentKinds vocabulary is required")
        if self._intents is None:
            raise ValueError("PolicyOptions.intents vocabulary is required")
        if self._actions.size < 1:
            raise ValueError("PolicyOptions.actions vocabulary must be non-empty")
        if self._argumentKinds.size < 1:
            raise ValueError("PolicyOptions.argumentKinds vocabulary must be non-empty")
        if self._intents.size < 1:
            raise ValueError("PolicyOptions.intents vocabulary must be non-empty")

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
    def actions(self) -> Optional[ActionVocabulary]:
        return self._actions

    @actions.setter
    def actions(self, value: Optional[ActionVocabulary]) -> None:
        self._actions = value

    @property
    def argumentKinds(self) -> Optional[ArgumentKindVocabulary]:
        return self._argumentKinds

    @argumentKinds.setter
    def argumentKinds(self, value: Optional[ArgumentKindVocabulary]) -> None:
        self._argumentKinds = value

    @property
    def intents(self) -> Optional[IntentVocabulary]:
        return self._intents

    @intents.setter
    def intents(self, value: Optional[IntentVocabulary]) -> None:
        self._intents = value

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
