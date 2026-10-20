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

# ==================================================================================
class Policy(nn.Module, iPolicy):
    def __init__(
        self, actRegEmbeddings: Tensor, 
        actKeys: Sequence[str] | None = None,
        featDim: int = C_DEFAULT_FEATURE_DIM, freeze: bool = True, 
        device: str | torch.device = "cuda"
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

        self._actionKeys: tuple[str, ...] = tuple(actKeys)
        mobileNet = models.mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.DEFAULT)

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
        self._head = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )

        self.register_buffer(
            "_registry",
            actRegEmbeddings.detach().to(self._device).clone(),
        )

        self.to(self._device)
    
    def forward(self, imageArray: Tensor) -> Tensor:
        """imageArray: [T,3,H,W] or [B,T,3,H,W] → embedding [B, embedDim]."""

        if imageArray.dim() == 4: imageArray = imageArray.unsqueeze(0)
        if imageArray.dim() != 5:
            raise ValueError(
                "Expected [T, 3, H, W] or [B, T, 3, H, W], "
                f"got shape {tuple(imageArray.shape)}"
            )

        imageArray = imageArray.to(device=self._device, dtype=torch.float32)
        batchSize, sequenceLength, channels, height, width = imageArray.shape
        if channels != 3: raise ValueError(f"Expected 3 channels, got {channels}")

        flat = imageArray.reshape(batchSize * sequenceLength, channels, height, width)

        if self._freezeBackbone:
            with torch.no_grad():
                features = self._backbone(flat)

        else:
            features = self._backbone(flat)

        features: Tensor = self._projection(features).view(batchSize, sequenceLength, -1)
        fused = features.mean(dim=1)
        embedding = F.normalize(self._head(fused), p=2, dim=-1)
        return embedding

    @torch.no_grad()
    def predict(self, imageArray: Tensor) -> str:
        wasTraining = self.training
        try:
            self.eval()
            embedding = self.forward(imageArray)
            scores = self._score(embedding)
            index = int(torch.argmax(scores, dim=-1).reshape(-1)[0].item())
            return self._actionKeys[index]
        
        finally:
            if wasTraining: self.train()

    def reset(self) -> None:
        pass

    def train(self, mode: bool = True) -> Policy:
        super().train(mode)
        if self._freezeBackbone: self._backbone.eval()
        return self

    def _score(self, embedding: Tensor) -> Tensor:
        if not hasattr(self, "_registry"): 
            raise RuntimeError(
                "Policy is not initialized with an action registry"
            )
        
        registry = F.normalize(self._registry, p=2, dim=-1)
        return torch.matmul(embedding, registry.T)
