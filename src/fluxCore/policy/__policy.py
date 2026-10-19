# ==================================================================================
# src/fluxCore/policy/__policy.py
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

# ==================================================================================
# Seed vocabulary only — not enforced as a fixed size. The live registry is authoritative.
C_SEED_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_DEFAULT_FEATURE_DIM: int = 512
C_DEFAULT_IMAGE_SIZE: int = 224


# ==================================================================================
class Policy(nn.Module, iPolicy):
    """Policy: array of images (one process) → one action via embedded registry.

    The action vocabulary is **volatile**. The registry size is not fixed at
    construction beyond matching the provided embeddings and keys. New actions
    can be introduced by extending the registry (and optionally fine-tuning
    only what changed). Old training samples do not need re-annotation solely
    because the vocabulary grew.
    """

    def __init__(
        self,
        actionRegistryEmbeddings: Tensor,
        actionKeys: Sequence[str] | None = None,
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

        numActions = int(actionRegistryEmbeddings.size(0))
        if numActions < 1:
            raise ValueError("Registry must contain at least one action")

        if actionKeys is None:
            if numActions <= len(C_SEED_ACTION_KEYS):
                actionKeys = C_SEED_ACTION_KEYS[:numActions]
            else:
                raise ValueError(
                    "actionKeys must be provided when registry size exceeds "
                    f"the seed vocabulary ({len(C_SEED_ACTION_KEYS)})"
                )
        else:
            actionKeys = tuple(actionKeys)

        if len(actionKeys) != numActions:
            raise ValueError(
                f"len(actionKeys)={len(actionKeys)} must equal "
                f"registry rows={numActions}"
            )

        self._actionKeys: tuple[str, ...] = tuple(actionKeys)

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

        self._proj = nn.Linear(576, featureDim)

        embedDim = int(actionRegistryEmbeddings.size(1))
        self._embedDim = embedDim
        self._head = nn.Sequential(
            nn.Linear(featureDim, featureDim),
            nn.ReLU(inplace=True),
            nn.Linear(featureDim, embedDim),
        )

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
        """Current vocabulary; length always matches the registry."""
        return self._actionKeys

    @property
    def numActions(self) -> int:
        return int(self._registry.size(0))

    def train(self, mode: bool = True) -> "Policy":
        super().train(mode)
        if self._freezeBackbone:
            self._backbone.eval()
        return self

    # ------------------------------------------------------------------
    def setRegistry(
        self,
        actionRegistryEmbeddings: Tensor,
        actionKeys: Sequence[str],
    ) -> None:
        """Replace or extend the outcome registry without rebuilding the backbone.

        Typical use when vocabulary grows:
        - append new rows to the embedding table
        - pass the full updated key list
        - optionally fine-tune only the head (and new rows), not the whole net

        Old samples keep their original labels; they do not need re-annotation
        merely because new actions were added elsewhere in the vocabulary.
        """
        if actionRegistryEmbeddings.dim() != 2:
            raise ValueError(
                "actionRegistryEmbeddings must have shape [numActions, embedDim]"
            )
        if actionRegistryEmbeddings.size(1) != self._embedDim:
            raise ValueError(
                f"embedDim mismatch: registry has {actionRegistryEmbeddings.size(1)}, "
                f"head expects {self._embedDim}"
            )
        keys = tuple(actionKeys)
        if len(keys) != actionRegistryEmbeddings.size(0):
            raise ValueError("actionKeys length must match registry rows")

        self._actionKeys = keys
        self._registry = actionRegistryEmbeddings.detach().to(self._device).clone()

    # ------------------------------------------------------------------
    def forward(self, imageArray: Tensor) -> Tensor:
        """Fuse an array of images into one embedding in registry space.

        imageArray shapes:
            [T, 3, H, W]     – one process
            [B, T, 3, H, W]  – batch of processes

        Returns:
            Normalized embedding [B, embedDim]
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

        flat = imageArray.reshape(batchSize * sequenceLength, channels, height, width)

        if self._freezeBackbone:
            with torch.no_grad():
                features = self._backbone(flat)
        else:
            features = self._backbone(flat)

        features = self._proj(features)
        features = features.view(batchSize, sequenceLength, -1)
        fused = features.mean(dim=1)

        embedding = self._head(fused)
        embedding = F.normalize(embedding, p=2, dim=-1)
        return embedding

    def score(self, embedding: Tensor) -> Tensor:
        """Cosine similarity against the current embedded outcome registry."""
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
            return self._actionKeys[index]
        finally:
            if wasTraining:
                self.train()

    def reset(self) -> None:
        """No internal state; kept for interface stability."""
        pass
