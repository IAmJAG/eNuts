# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Sequence

# ==================================================================================
from torch import Tensor

# ==================================================================================
C_SEED_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_DEFAULT_FEATURE_DIM: int = 512
C_ARG_KINDS: tuple[str, ...] = ("coordinate", "box", "key", "text")


# ==================================================================================
class RegistryOptions:
    """Labels + embeddings for one discrete registry (action, key, or text)."""

    def __init__(self, embeddings: Tensor, labels: Sequence[str]) -> None:
        if embeddings.dim() != 2:
            raise ValueError("embeddings must have shape [N, embedDim]")
        
        if embeddings.size(0) < 1:
            raise ValueError("embeddings must contain at least one row")
        
        labels = tuple(labels)
        if len(labels) != embeddings.size(0):
            raise ValueError("labels length must match embeddings rows")

        self._embeddings = embeddings
        self._labels = labels

    @property
    def embeddings(self) -> Tensor:
        return self._embeddings

    @property
    def labels(self) -> tuple[str, ...]:
        return self._labels

    @property
    def embedDim(self) -> int:
        return int(self._embeddings.size(1))

    @property
    def size(self) -> int:
        return int(self._embeddings.size(0))


# ==================================================================================
class PolicyOptions:
    """Construction details for Policy: registries + model settings.

    - action: required (labels + embeddings)
    - argKinds: argument kinds the kind-head may emit
    - key / text: optional registries for key-code and text selection
    """

    def __init__(
        self, action: RegistryOptions, key: RegistryOptions | None = None,
        text: RegistryOptions | None = None, argKinds: Sequence[str] = C_ARG_KINDS,
        featureDim: int = C_DEFAULT_FEATURE_DIM, freezeBackbone: bool = True,
        device: str = "cuda",
    ) -> None:
        kinds = tuple(argKinds)
        if not kinds:
            raise ValueError("argKinds must be non-empty")
        
        for kind in kinds:
            if kind not in C_ARG_KINDS:
                raise ValueError(f"unknown arg kind: {kind!r}")

        if key is not None and key.embedDim != action.embedDim:
            raise ValueError("key embedDim must match action embedDim")
        
        if text is not None and text.embedDim != action.embedDim:
            raise ValueError("text embedDim must match action embedDim")

        self._action = action
        self._key = key
        self._text = text
        self._argKinds = kinds
        self._featureDim = int(featureDim)
        self._freezeBackbone = bool(freezeBackbone)
        self._device = device

    @property
    def action(self) -> RegistryOptions:
        return self._action

    @property
    def key(self) -> RegistryOptions | None:
        return self._key

    @property
    def text(self) -> RegistryOptions | None:
        return self._text

    @property
    def argKinds(self) -> tuple[str, ...]:
        return self._argKinds

    @property
    def featureDim(self) -> int:
        return self._featureDim

    @property
    def freezeBackbone(self) -> bool:
        return self._freezeBackbone

    @property
    def device(self) -> str:
        return self._device

    @property
    def embedDim(self) -> int:
        return self._action.embedDim
