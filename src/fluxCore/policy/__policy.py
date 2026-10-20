# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any

# ==================================================================================
import torch
import torch.nn as nn
import torch.nn.functional as F

# ==================================================================================
from torch import Tensor
from torch import device as TorchDevice
from torchvision import models
from torchvision.models import MobileNet_V3_Small_Weights

# ==================================================================================
from ..types.interface.policy import iPolicy
from ..utilities import getTorchDevice
from .__policyOptions import PolicyOptions


# ==================================================================================
class Policy(nn.Module, iPolicy):
    def __init__(self, options: PolicyOptions) -> None:
        super().__init__()

        actions = options.requireActions()
        argumentKinds = options.requireArgumentKinds()

        self._device: TorchDevice = getTorchDevice(options.device)
        self._actionLabels = actions.labels
        self._argumentKindLabels = argumentKinds.labels
        self._embedDim = options.embedDim
        self._freezeBackbone = options.freezeBackbone

        self.register_buffer(
            "_actionEmbeddings",
            options.actionEmbeddings().detach().to(self._device).clone(),
        )
        self.register_buffer(
            "_argumentKindEmbeddings",
            options.argumentKindEmbeddings().detach().to(self._device).clone(),
        )

        mobileNet = models.mobilenet_v3_small(
            weights=MobileNet_V3_Small_Weights.DEFAULT
        )
        self._backbone = nn.Sequential(
            mobileNet.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        if self._freezeBackbone:
            for parameter in self._backbone.parameters():
                parameter.requires_grad = False

        featDim = options.featureDim
        self._projection = nn.Linear(576, featDim)

        self._actionHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )
        self._argumentKindHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, self._embedDim),
        )
        # Continuous spatial payload for coordinate / box (normalized [0, 1])
        self._spatialHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, 4),
            nn.Sigmoid(),
        )

        self.to(self._device)

    # ------------------------------------------------------------------
    @property
    def actionKeys(self) -> tuple[str, ...]:
        return self._actionLabels

    def forward(self, imageArray: Tensor) -> dict[str, Tensor]:
        fused = self._fuse(imageArray)
        return {
            "actionEmbedding": F.normalize(self._actionHead(fused), p=2, dim=-1),
            "argumentKindEmbedding": F.normalize(
                self._argumentKindHead(fused), p=2, dim=-1
            ),
            "spatial": self._spatialHead(fused),
        }

    @torch.no_grad()
    def predict(self, imageArray: Tensor) -> tuple[str, dict[str, Any]]:
        wasTraining = self.training
        try:
            self.eval()
            out = self.forward(imageArray)

            actionScores = self._cosine(out["actionEmbedding"], self._actionEmbeddings)
            actionIndex = int(torch.argmax(actionScores, dim=-1).reshape(-1)[0].item())
            actionKey = self._actionLabels[actionIndex]

            kindScores = self._cosine(
                out["argumentKindEmbedding"], self._argumentKindEmbeddings
            )
            kindIndex = int(torch.argmax(kindScores, dim=-1).reshape(-1)[0].item())
            kind = self._argumentKindLabels[kindIndex]

            spatial = out["spatial"].reshape(-1, 4)[0].detach().cpu()
            argument = self._buildArgument(kind, spatial)
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
    def _cosine(embedding: Tensor, table: Tensor) -> Tensor:
        if table.numel() == 0:
            return embedding.new_zeros(embedding.size(0), 0)
        emb = F.normalize(embedding, p=2, dim=-1)
        reg = F.normalize(table, p=2, dim=-1)
        return torch.matmul(emb, reg.T)

    def _buildArgument(self, kind: str, spatial: Tensor) -> dict[str, Any]:
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
            # Open-ended value — not selected from a closed vocabulary.
            return {"kind": "key", "code": ""}
        if kind == "text":
            # Open-ended value — not selected from a closed vocabulary.
            return {"kind": "text", "value": ""}
        return {"kind": kind}
