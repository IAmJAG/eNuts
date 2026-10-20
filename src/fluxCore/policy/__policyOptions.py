# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from .__vocabulary import C_DEFAULT_EMBED_DIM, Vocabulary, VocabularyItem

# ==================================================================================
C_SEED_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_SEED_ACTION_DESCRIPTIONS: tuple[str, ...] = (
    "finger/right mouse button down",
    "finger/right mouse button up",
    "finger/mouse move",
    "send key or text",
)
C_SEED_ARGUMENT_KINDS: tuple[str, ...] = ("coordinate", "box", "key", "text")
C_SEED_ARGUMENT_KIND_DESCRIPTIONS: tuple[str, ...] = (
    "normalized point (x, y)",
    "normalized box (left, top, width, height)",
    "keyboard key code (open-ended value)",
    "text string (open-ended value)",
)
C_DEFAULT_FEATURE_DIM: int = 512


# ==================================================================================
class PolicyOptions(Serializable):
    def __init__(
        self, actions: Optional[Vocabulary], argument: Optional[Vocabulary],
        featureDim: int = C_DEFAULT_FEATURE_DIM, freezeBackbone: bool = True,
        embedDim: int = C_DEFAULT_EMBED_DIM, device: str = "cuda"
    ) -> None:
        super().__init__()
        self._actions: Optional[Vocabulary] = actions
        self._argumentKinds: Optional[Vocabulary] = argument
        self._featureDim: int = int(featureDim)
        self._freezeBackbone: bool = bool(freezeBackbone)
        self._device: str = device if device is not None else "cuda"
        self._embedDim: int = int(embedDim)

        self.Properties.extend(
            [
                "actions",
                "argumentKinds",
                "featureDim",
                "freezeBackbone",
                "device",
                "embedDim",
            ]
        )
        self._validate()

    def _validate(self) -> None:
        if self._featureDim < 1:
            raise ValueError("featureDim must be >= 1")
        if self._embedDim < 1:
            raise ValueError("embedDim must be >= 1")

        if self._actions is not None:
            self._actions.embedDim = self._embedDim
            if self._actions.size < 1:
                raise ValueError("actions vocabulary must contain at least one item")

        if self._argumentKinds is not None:
            self._argumentKinds.embedDim = self._embedDim
            if self._argumentKinds.size < 1:
                raise ValueError("argumentKinds vocabulary must contain at least one item")

    # ------------------------------------------------------------------
    @property
    def actions(self) -> Vocabulary | None:
        return self._actions

    @actions.setter
    def actions(self, value: Vocabulary | None) -> None:
        self._actions = value
        self._validate()

    @property
    def argumentKinds(self) -> Vocabulary | None:
        return self._argumentKinds

    @argumentKinds.setter
    def argumentKinds(self, value: Vocabulary | None) -> None:
        self._argumentKinds = value
        self._validate()

    @property
    def featureDim(self) -> int:
        return self._featureDim

    @featureDim.setter
    def featureDim(self, value: int) -> None:
        self._featureDim = int(value)
        self._validate()

    @property
    def freezeBackbone(self) -> bool:
        return self._freezeBackbone

    @freezeBackbone.setter
    def freezeBackbone(self, value: bool) -> None:
        self._freezeBackbone = bool(value)

    @property
    def device(self) -> str:
        return self._device

    @device.setter
    def device(self, value: str) -> None:
        self._device = value if value is not None else "cuda"

    @property
    def embedDim(self) -> int:
        return self._embedDim

    @embedDim.setter
    def embedDim(self, value: int) -> None:
        self._embedDim = int(value)
        self._validate()

    # ------------------------------------------------------------------
    def requireActions(self) -> Vocabulary:
        if self._actions is None or self._actions.size < 1:
            raise ValueError("PolicyOptions.actions is required")
        return self._actions

    def requireArgumentKinds(self) -> Vocabulary:
        if self._argumentKinds is None or self._argumentKinds.size < 1:
            raise ValueError("PolicyOptions.argumentKinds is required")
        return self._argumentKinds

    def actionEmbeddings(self) -> Tensor:
        return self.requireActions().toEmbeddings()

    def argumentKindEmbeddings(self) -> Tensor:
        return self.requireArgumentKinds().toEmbeddings()

    @classmethod
    def withDefaults(
        cls,
        featureDim: int = C_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        device: str = "cuda",
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> PolicyOptions:
        """Build options with seed action and argument-kind vocabularies."""
        actions = Vocabulary.fromLabels(
            C_SEED_ACTION_KEYS,
            C_SEED_ACTION_DESCRIPTIONS,
            embedDim=embedDim,
        )
        argumentKinds = Vocabulary.fromLabels(
            C_SEED_ARGUMENT_KINDS,
            C_SEED_ARGUMENT_KIND_DESCRIPTIONS,
            embedDim=embedDim,
        )
        return cls(
            actions=actions,
            argumentKinds=argumentKinds,
            featureDim=featureDim,
            freezeBackbone=freezeBackbone,
            device=device,
            embedDim=embedDim,
        )
