# ==================================================================================
# src/fluxCore/policy/__policy.py
# ==================================================================================
from typing import Any

# ==================================================================================
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torchvision import models
from torchvision.models import MobileNet_V3_Small_Weights

# ==================================================================================
from ..types.interface.policy import iPolicy

# ==================================================================================
C_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_NUM_ACTIONS: int = len(C_ACTION_KEYS)
C_DEFAULT_FEATURE_DIM: int = 512
C_DEFAULT_IMAGE_SIZE: int = 224


# ==================================================================================
class Policy(nn.Module, iPolicy):
    """Policy that treats an array of images as one process and predicts one action.

    - Input: array of images  [T, 3, H, W]  (or batch of arrays [B, T, 3, H, W])
    - Backbone: MobileNetV3-Small with proven ImageNet weights
    - Head: owned by this class, projects into an embedded outcome registry
    - Output: one action key per array (cosine similarity against the registry)
    """

    def __init__(
        self,
        actionRegistryEmbeddings: Tensor,
        featureDim: int = C_DEFAULT_FEATURE_DIM,
        freezeBackbone: bool = True,
        device: str | torch.device = "cpu",
    ) -> None:
        super().__init__()

        if isinstance(device, str):
            if device.lower().startswith("cuda") and not torch.cuda.is_available():
                device = "cpu"
            self._device = torch.device(device)
        else:
            self._device = device

        if actionRegistryEmbeddings.dim() != 2:
            raise ValueError(
                "actionRegistryEmbeddings must have shape [numActions, embedDim]"
            )
        if actionRegistryEmbeddings.size(0) != C_NUM_ACTIONS:
            raise ValueError(
                f"Registry must contain exactly {C_NUM_ACTIONS} entries "
                f"(got {actionRegistryEmbeddings.size(0)})"
            )

        # ------------------------------------------------------------------
        # Proven backbone (MobileNetV3-Small weights)
        # ------------------------------------------------------------------
        mobileNet = models.mobilenet_v3_small(
            weights=MobileNet_V3_Small_Weights.DEFAULT
        )
        self._backbone = nn.Sequential(
            mobileNet.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )

        self._freezeBackbone = freezeBackbone
        if freezeBackbone:
            for parameter in self._backbone.parameters():
                parameter.requires_grad = False

        # 576 is the channel count of MobileNetV3-Small final feature map
        self._proj = nn.Linear(576, featureDim)

        # Own head → registry embedding space
        embedDim = actionRegistryEmbeddings.size(1)
        self._head = nn.Sequential(
            nn.Linear(featureDim, featureDim),
            nn.ReLU(inplace=True),
            nn.Linear(featureDim, embedDim),
        )

        # Immutable embedded outcome registry
        self.register_buffer(
            "_registry",
            actionRegistryEmbeddings.detach().to(self._device).clone(),
        )

        self.to(self._device)

    # ------------------------------------------------------------------
    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def actionKeys(self) -> tuple[str, ...]:
        return C_ACTION_KEYS

    def train(self, mode: bool = True) -> "Policy":
        super().train(mode)
        if self._freezeBackbone:
            self._backbone.eval()
        return self

    # ------------------------------------------------------------------
    def forward(self, imageArray: Tensor) -> Tensor:
        """Fuse an array of images into one embedding in registry space.

        imageArray shapes accepted:
            [T, 3, H, W]     – one process
            [B, T, 3, H, W]  – batch of processes

        Returns:
            Normalized embedding of shape [B, embedDim]
        """
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

        # Run every frame through the backbone
        flat = imageArray.reshape(batchSize * sequenceLength, channels, height, width)

        if self._freezeBackbone:
            with torch.no_grad():
                features = self._backbone(flat)
        else:
            features = self._backbone(flat)

        features = self._proj(features)
        features = features.view(batchSize, sequenceLength, -1)

        # Fuse the T frames of each process into one vector
        fused = features.mean(dim=1)

        embedding = self._head(fused)
        embedding = F.normalize(embedding, p=2, dim=-1)
        return embedding

    def score(self, embedding: Tensor) -> Tensor:
        """Cosine similarity against the embedded outcome registry."""
        registry = F.normalize(self._registry, p=2, dim=-1)
        return torch.matmul(embedding, registry.T)

    @torch.no_grad()
    def predict(self, imageArray: Tensor) -> str:
        """Return the action key for one image array (one process → one result)."""
        wasTraining = self.training
        try:
            self.eval()
            embedding = self.forward(imageArray)
            scores = self.score(embedding)
            index = int(torch.argmax(scores, dim=-1).reshape(-1)[0].item())
            return C_ACTION_KEYS[index]
        finally:
            if wasTraining:
                self.train()

    def reset(self) -> None:
        """No internal state; kept for interface stability."""
        pass
