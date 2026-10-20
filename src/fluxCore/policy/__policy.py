# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Sequence

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
# Continuous argument layout (normalized [0, 1]):
#   [0]=x or left, [1]=y or top, [2]=width (box), [3]=height (box)
# coordinate actions use the first two; box actions use all four.
C_DEFAULT_ARG_DIM: int = 4


# ==================================================================================
class Policy(nn.Module, iPolicy):
    """Array of images (one process) → action key + argument vector.

    Action: cosine score against a dynamic embedded registry (volatile vocabulary).
    Arguments: continuous vector in [0, 1] (spatial payload for the chosen action).
    """

    def __init__(
        self,
        actRegEmbeddings: Tensor,
        actKeys: Sequence[str] | None = None,
        featDim: int = C_DEFAULT_FEATURE_DIM,
        argDim: int = C_DEFAULT_ARG_DIM,
        freeze: bool = True,
        device: str | torch.device = "cuda",
    ) -> None:
        super().__init__()
        self._device = getTorchDevice(device)

        if actRegEmbeddings.dim() != 2:
            raise ValueError(
                "Action Registry Embedding must have shape [numActions, embedDim]"
            )

        numActions = int(actRegEmbeddings.size(0))
        if numActions < 1:
            raise ValueError("Registry must contain at least one action")

        if actKeys is None:
            if numActions <= len(C_SEED_ACTION_KEYS):
                actKeys = C_SEED_ACTION_KEYS[:numActions]
            else:
                raise ValueError(
                    "actionKeys must be provided when registry size exceeds "
                    f"the seed vocabulary ({len(C_SEED_ACTION_KEYS)})"
                )
        else:
            actKeys = tuple(actKeys)

        if len(actKeys) != numActions:
            raise ValueError(
                f"len(actionKeys)={len(actKeys)} must equal registry rows={numActions}"
            )

        if argDim < 1:
            raise ValueError("argDim must be >= 1")

        self._actionKeys: tuple[str, ...] = tuple(actKeys)
        self._argDim = int(argDim)

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
        self._embedDim: int = int(actRegEmbeddings.size(1))

        # Discrete action head → registry space
        self._actionHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )

        # Continuous argument head → normalized spatial / payload vector
        self._argHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._argDim),
            nn.Sigmoid(),
        )

        self.register_buffer(
            "_registry",
            actRegEmbeddings.detach().to(self._device).clone(),
        )

        self.to(self._device)

    # ------------------------------------------------------------------
    @property
    def actionKeys(self) -> tuple[str, ...]:
        return self._actionKeys

    def setRegistry(
        self,
        actRegEmbeddings: Tensor,
        actKeys: Sequence[str],
    ) -> None:
        """Grow or replace action vocabulary; embedDim must stay the same."""
        if actRegEmbeddings.dim() != 2:
            raise ValueError(
                "Action Registry Embedding must have shape [numActions, embedDim]"
            )
        if actRegEmbeddings.size(1) != self._embedDim:
            raise ValueError(
                f"embedDim mismatch: registry has {actRegEmbeddings.size(1)}, "
                f"head expects {self._embedDim}"
            )
        keys = tuple(actKeys)
        if len(keys) != actRegEmbeddings.size(0):
            raise ValueError("actionKeys length must match registry rows")

        self._actionKeys = keys
        self._registry = actRegEmbeddings.detach().to(self._device).clone()

    def forward(self, imageArray: Tensor) -> tuple[Tensor, Tensor]:
        """Returns (actionEmbedding [B, embedDim], arguments [B, argDim])."""
        fused = self._fuse(imageArray)

        actionEmbedding = F.normalize(self._actionHead(fused), p=2, dim=-1)
        arguments = self._argHead(fused)
        return actionEmbedding, arguments

    @torch.no_grad()
    def predict(self, imageArray: Tensor) -> tuple[str, Tensor]:
        """One process → (action key, argument vector [argDim])."""
        wasTraining = self.training
        try:
            self.eval()
            actionEmbedding, arguments = self.forward(imageArray)
            scores = self._score(actionEmbedding)
            index = int(torch.argmax(scores, dim=-1).reshape(-1)[0].item())
            args = arguments.reshape(-1, self._argDim)[0].detach().cpu()
            return self._actionKeys[index], args
        finally:
            if wasTraining:
                self.train()

    def train(self, mode: bool = True) -> Policy:
        super().train(mode)
        if self._freezeBackbone:
            self._backbone.eval()
        return self

    # ------------------------------------------------------------------
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

    def _score(self, embedding: Tensor) -> Tensor:
        if not hasattr(self, "_registry"):
            raise RuntimeError("Policy is not initialized with an action registry")
        registry = F.normalize(self._registry, p=2, dim=-1)
        return torch.matmul(embedding, registry.T)
