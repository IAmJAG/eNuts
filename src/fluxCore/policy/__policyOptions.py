# ==================================================================================
from __future__ import annotations

# ==================================================================================
import hashlib
from typing import Sequence

# ==================================================================================
import torch
import torch.nn.functional as F
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
C_SEED_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_DEFAULT_FEATURE_DIM: int = 512
C_DEFAULT_EMBED_DIM: int = 128
C_ARG_KINDS: tuple[str, ...] = ("coordinate", "box", "key", "text")


# ==================================================================================
def labelsToEmbeddings(labels: Sequence[str], embedDim: int) -> Tensor:
    """Deterministic unit embeddings from label strings (stable across processes)."""
    if embedDim < 1:
        raise ValueError("embedDim must be >= 1")
    rows: list[Tensor] = []
    for label in labels:
        digest = hashlib.sha256(str(label).encode("utf-8")).hexdigest()
        seed = int(digest[:16], 16) % (2**63 - 1)
        generator = torch.Generator()
        generator.manual_seed(seed)
        vector = torch.randn(embedDim, generator=generator, dtype=torch.float32)
        rows.append(F.normalize(vector, p=2, dim=0))
    if not rows:
        return torch.empty(0, embedDim, dtype=torch.float32)
    return torch.stack(rows, dim=0)


# ==================================================================================
class RegistryOptions(Serializable):
    """Serializable discrete registry: labels (+ optional descriptions) → embeddings.

    Embeddings are not persisted. They are produced by :meth:`embeddings` from
    the label list so options files stay compact and human-editable.
    """

    def __init__(
        self,
        labels: Sequence[str] | None = None,
        descriptions: Sequence[str] | None = None,
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()
        self._labels: list[str] = list(labels) if labels is not None else []
        self._descriptions: list[str] = (
            list(descriptions) if descriptions is not None else []
        )
        self._embedDim: int = int(embedDim)
        self.Properties.extend(["labels", "descriptions", "embedDim"])
        self._validate()

    def _validate(self) -> None:
        if self._embedDim < 1:
            raise ValueError("embedDim must be >= 1")
        if self._descriptions and len(self._descriptions) != len(self._labels):
            raise ValueError("descriptions length must match labels length when provided")

    # ------------------------------------------------------------------
    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(self._labels)

    @labels.setter
    def labels(self, value: Sequence[str]) -> None:
        self._labels = list(value) if value is not None else []
        self._validate()

    @property
    def descriptions(self) -> tuple[str, ...]:
        return tuple(self._descriptions)

    @descriptions.setter
    def descriptions(self, value: Sequence[str]) -> None:
        self._descriptions = list(value) if value is not None else []
        self._validate()

    @property
    def embedDim(self) -> int:
        return self._embedDim

    @embedDim.setter
    def embedDim(self, value: int) -> None:
        self._embedDim = int(value)
        self._validate()

    @property
    def size(self) -> int:
        return len(self._labels)

    def embeddings(self) -> Tensor:
        """Build [N, embedDim] embeddings from labels."""
        if not self._labels:
            return torch.empty(0, self._embedDim, dtype=torch.float32)
        return labelsToEmbeddings(self._labels, self._embedDim)


# ==================================================================================
class PolicyOptions(Serializable):
    """Serializable policy construction options.

    Persist labels and settings to JSON via :meth:`encode` / :meth:`decode`.
    Registries convert labels to embedding tensors when the policy is built.
    """

    def __init__(
        self,
        action: RegistryOptions | None = None,
        key: RegistryOptions | None = None,
        text: RegistryOptions | None = None,
        argKinds: Sequence[str] | None = None,
        featureDim: int = C_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        device: str = "cuda",
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()

        self._action: RegistryOptions | None = action
        self._key: RegistryOptions | None = key
        self._text: RegistryOptions | None = text
        self._argKinds: list[str] = (
            list(argKinds) if argKinds is not None else list(C_ARG_KINDS)
        )
        self._featureDim: int = int(featureDim)
        self._freezeBackbone: bool = bool(freezeBackbone)
        self._device: str = device if device is not None else "cuda"
        self._embedDim: int = int(embedDim)

        self.Properties.extend(
            [
                "action",
                "key",
                "text",
                "argKinds",
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
        if not self._argKinds:
            raise ValueError("argKinds must be non-empty")
        for kind in self._argKinds:
            if kind not in C_ARG_KINDS:
                raise ValueError(f"unknown arg kind: {kind!r}")

        if self._action is not None:
            if self._action.embedDim != self._embedDim:
                self._action.embedDim = self._embedDim
            if self._action.size < 1:
                raise ValueError("action registry must contain at least one label")

        if self._key is not None and self._key.embedDim != self._embedDim:
            self._key.embedDim = self._embedDim
        if self._text is not None and self._text.embedDim != self._embedDim:
            self._text.embedDim = self._embedDim

    # ------------------------------------------------------------------
    @property
    def action(self) -> RegistryOptions | None:
        return self._action

    @action.setter
    def action(self, value: RegistryOptions | None) -> None:
        self._action = value
        self._validate()

    @property
    def key(self) -> RegistryOptions | None:
        return self._key

    @key.setter
    def key(self, value: RegistryOptions | None) -> None:
        self._key = value
        self._validate()

    @property
    def text(self) -> RegistryOptions | None:
        return self._text

    @text.setter
    def text(self, value: RegistryOptions | None) -> None:
        self._text = value
        self._validate()

    @property
    def argKinds(self) -> tuple[str, ...]:
        return tuple(self._argKinds)

    @argKinds.setter
    def argKinds(self, value: Sequence[str]) -> None:
        self._argKinds = list(value) if value is not None else list(C_ARG_KINDS)
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
    def requireAction(self) -> RegistryOptions:
        if self._action is None or self._action.size < 1:
            raise ValueError("PolicyOptions.action is required and must have labels")
        return self._action

    def actionEmbeddings(self) -> Tensor:
        return self.requireAction().embeddings()

    def keyEmbeddings(self) -> Tensor | None:
        if self._key is None or self._key.size < 1:
            return None
        return self._key.embeddings()

    def textEmbeddings(self) -> Tensor | None:
        if self._text is None or self._text.size < 1:
            return None
        return self._text.embeddings()
