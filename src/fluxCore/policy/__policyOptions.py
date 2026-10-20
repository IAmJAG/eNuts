# ==================================================================================
from __future__ import annotations

# ==================================================================================
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from .vocabulary import C_DEFAULT_EMBED_DIM, Vocabulary

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
    """Serializable policy options.

    Discrete vocabularies only:
      - actions
      - argumentKinds

    Argument values (coords, key codes, free text) are not vocabularies.
    """

    def __init__(
        self,
        actions: Vocabulary | None = None,
        argumentKinds: Vocabulary | None = None,
        featureDim: int = C_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        device: str = "cuda",
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()

        self._actions: Vocabulary | None = actions
        self._argumentKinds: Vocabulary | None = argumentKinds
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
            if self._actions.dimension < 1:
                raise ValueError("actions vocabulary must be non-empty")

        if self._argumentKinds is not None:
            self._argumentKinds.embedDim = self._embedDim
            if self._argumentKinds.dimension < 1:
                raise ValueError("argumentKinds vocabulary must be non-empty")

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
        if self._actions is None or self._actions.dimension < 1:
            raise ValueError("PolicyOptions.actions is required")
        return self._actions

    def requireArgumentKinds(self) -> Vocabulary:
        if self._argumentKinds is None or self._argumentKinds.dimension < 1:
            raise ValueError("PolicyOptions.argumentKinds is required")
        return self._argumentKinds

    def actionEmbeddings(self) -> Tensor:
        return self.requireActions().toTensor()

    def argumentKindEmbeddings(self) -> Tensor:
        return self.requireArgumentKinds().toTensor()

    @classmethod
    def withDefaults(
        cls,
        featureDim: int = C_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        device: str = "cuda",
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> PolicyOptions:
        return cls(
            actions=Vocabulary(C_SEED_ACTIONS, embedDim=embedDim),
            argumentKinds=Vocabulary(C_SEED_ARGUMENT_KINDS, embedDim=embedDim),
            featureDim=featureDim,
            freezeBackbone=freezeBackbone,
            device=device,
            embedDim=embedDim,
        )
