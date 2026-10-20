# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Sequence

# ==================================================================================
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torchvision import models
from torchvision.models import MobileNet_V3_Small_Weights

# ==================================================================================
from ..types.interface.policy import iPolicy
from ..utilities import getTorchDevice

# ==================================================================================
C_SEED_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_DEFAULT_FEATURE_DIM: int = 512
C_ARG_KINDS: tuple[str, ...] = ("coordinate", "box", "key", "text")


# ==================================================================================
class Policy(nn.Module, iPolicy):
    """Array of images (one process) → action key + variant argument.

    Registries (actions, optional keys, optional texts) are fixed at construction.
    Vocabulary changes are a planning/training concern: build a new Policy (or
    load a checkpoint trained for that vocabulary). No runtime setRegistry.

    Argument kinds:
      coordinate → {kind, x, y}           normalized [0, 1]
      box        → {kind, top, left, width, height}
      key        → {kind, code}           from key registry supplied at init
      text       → {kind, value}          from text registry supplied at init
    """

    def __init__(
        self,
        actRegEmbeddings: Tensor,
        actKeys: Sequence[str] | None = None,
        keyRegEmbeddings: Tensor | None = None,
        keyCodes: Sequence[str] | None = None,
        textRegEmbeddings: Tensor | None = None,
        textValues: Sequence[str] | None = None,
        featDim: int = C_DEFAULT_FEATURE_DIM,
        freeze: bool = True,
        device: str | torch.device = "cuda",
    ) -> None:
        super().__init__()
        self._device = getTorchDevice(device)

        self._actionKeys = self._bindRegistry(
            actRegEmbeddings, actKeys, C_SEED_ACTION_KEYS, "action"
        )
        self.register_buffer(
            "_actionRegistry",
            actRegEmbeddings.detach().to(self._device).clone(),
        )
        self._embedDim = int(actRegEmbeddings.size(1))

        self._keyCodes: tuple[str, ...] = ()
        if keyRegEmbeddings is not None:
            self._keyCodes = self._bindRegistry(
                keyRegEmbeddings, keyCodes, (), "key"
            )
            if keyRegEmbeddings.size(1) != self._embedDim:
                raise ValueError("key registry embedDim must match action embedDim")
            self.register_buffer(
                "_keyRegistry",
                keyRegEmbeddings.detach().to(self._device).clone(),
            )
        else:
            self.register_buffer("_keyRegistry", torch.empty(0, self._embedDim))

        self._textValues: tuple[str, ...] = ()
        if textRegEmbeddings is not None:
            self._textValues = self._bindRegistry(
                textRegEmbeddings, textValues, (), "text"
            )
            if textRegEmbeddings.size(1) != self._embedDim:
                raise ValueError("text registry embedDim must match action embedDim")
            self.register_buffer(
                "_textRegistry",
                textRegEmbeddings.detach().to(self._device).clone(),
            )
        else:
            self.register_buffer("_textRegistry", torch.empty(0, self._embedDim))

        mobileNet = models.mobilenet_v3_small(
            weights=MobileNet_V3_Small_Weights.DEFAULT
        )
        self._backbone = nn.Sequential(
            mobileNet.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        self._freezeBackbone = freeze
        if freeze:
            for parameter in self._backbone.parameters():
                parameter.requires_grad = False

        self._projection = nn.Linear(576, featDim)

        self._actionHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )
        self._argKindHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, len(C_ARG_KINDS)),
        )
        self._spatialHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, 4),
            nn.Sigmoid(),
        )
        self._keyHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )
        self._textHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )

        self.to(self._device)

    # ------------------------------------------------------------------
    @property
    def actionKeys(self) -> tuple[str, ...]:
        return self._actionKeys

    def forward(self, imageArray: Tensor) -> dict[str, Tensor]:
        """Training forward. All tensors batched on the model device."""
        fused = self._fuse(imageArray)
        return {
            "actionEmbedding": F.normalize(self._actionHead(fused), p=2, dim=-1),
            "argKindLogits": self._argKindHead(fused),
            "spatial": self._spatialHead(fused),
            "keyEmbedding": F.normalize(self._keyHead(fused), p=2, dim=-1),
            "textEmbedding": F.normalize(self._textHead(fused), p=2, dim=-1),
        }

    @torch.no_grad()
    def predict(self, imageArray: Tensor) -> tuple[str, dict[str, Any]]:
        """One process → (actionKey, argument dict)."""
        wasTraining = self.training
        try:
            self.eval()
            out = self.forward(imageArray)

            actionScores = self._cosine(
                out["actionEmbedding"], self._actionRegistry
            )
            actionIndex = int(torch.argmax(actionScores, dim=-1).reshape(-1)[0].item())
            actionKey = self._actionKeys[actionIndex]

            kindIndex = int(
                torch.argmax(out["argKindLogits"], dim=-1).reshape(-1)[0].item()
            )
            kind = C_ARG_KINDS[kindIndex]
            spatial = out["spatial"].reshape(-1, 4)[0].detach().cpu()

            argument = self._buildArgument(
                kind,
                spatial,
                out["keyEmbedding"],
                out["textEmbedding"],
            )
            return actionKey, argument
        finally:
            if wasTraining:
                self.train()

    def train(self, mode: bool = True) -> Policy:
        super().train(mode)
        if self._freezeBackbone:
            self._backbone.eval()
        return self

    # ------------------------------------------------------------------
    @staticmethod
    def _bindRegistry(
        embeddings: Tensor,
        labels: Sequence[str] | None,
        seed: Sequence[str],
        name: str,
    ) -> tuple[str, ...]:
        if embeddings.dim() != 2:
            raise ValueError(f"{name} registry must have shape [N, embedDim]")
        n = int(embeddings.size(0))
        if n < 1:
            raise ValueError(f"{name} registry must contain at least one entry")

        if labels is None:
            if seed and n <= len(seed):
                labels = tuple(seed[:n])
            else:
                raise ValueError(f"{name} labels must be provided for this registry size")
        else:
            labels = tuple(labels)

        if len(labels) != n:
            raise ValueError(f"{name} labels length must match registry rows")
        return labels

    def _fuse(self, imageArray: Tensor) -> Tensor:
        if imageArray.dim() == 4:
            imageArray = imageArray.unsqueeze(0)
        if imageArray.dim() != 5:
            raise ValueError(
                "Expected [T, 3, H, W] or [B, T, 3, H, W], "
                f"got shape {tuple(imageArray.shape)}"
            )

        imageArray = imageArray.to(device=self._device, dtype=torch.float32)
        batchSize, sequenceLength, channels, height, width = imageArray.shape
        if channels != 3:
            raise ValueError(f"Expected 3 channels, got {channels}")

        flat = imageArray.reshape(batchSize * sequenceLength, channels, height, width)
        if self._freezeBackbone:
            with torch.no_grad():
                features = self._backbone(flat)
        else:
            features = self._backbone(flat)

        features = self._projection(features).view(batchSize, sequenceLength, -1)
        return features.mean(dim=1)

    @staticmethod
    def _cosine(embedding: Tensor, registry: Tensor) -> Tensor:
        if registry.numel() == 0:
            return embedding.new_zeros(embedding.size(0), 0)
        emb = F.normalize(embedding, p=2, dim=-1)
        reg = F.normalize(registry, p=2, dim=-1)
        return torch.matmul(emb, reg.T)

    def _buildArgument(
        self,
        kind: str,
        spatial: Tensor,
        keyEmbedding: Tensor,
        textEmbedding: Tensor,
    ) -> dict[str, Any]:
        if kind == "coordinate":
            return {
                "kind": "coordinate",
                "x": float(spatial[0]),
                "y": float(spatial[1]),
            }
        if kind == "box":
            return {
                "kind": "box",
                "left": float(spatial[0]),
                "top": float(spatial[1]),
                "width": float(spatial[2]),
                "height": float(spatial[3]),
            }
        if kind == "key":
            if self._keyRegistry.numel() == 0 or not self._keyCodes:
                return {"kind": "key", "code": ""}
            scores = self._cosine(keyEmbedding, self._keyRegistry)
            index = int(torch.argmax(scores, dim=-1).reshape(-1)[0].item())
            return {"kind": "key", "code": self._keyCodes[index]}
        if kind == "text":
            if self._textRegistry.numel() == 0 or not self._textValues:
                return {"kind": "text", "value": ""}
            scores = self._cosine(textEmbedding, self._textRegistry)
            index = int(torch.argmax(scores, dim=-1).reshape(-1)[0].item())
            return {"kind": "text", "value": self._textValues[index]}
        return {"kind": kind}
