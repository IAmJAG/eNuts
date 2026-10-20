# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any

# ==================================================================================
import torch
import torch.nn as nn
import torch.nn.functional as F
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

        action = options.requireAction()

        self._device: TorchDevice = getTorchDevice(options.device)
        self._argKinds = options.argKinds
        self._actionKeys = action.labels
        self._keyCodes = options.key.labels if options.key is not None else ()
        self._textValues = options.text.labels if options.text is not None else ()
        self._embedDim = options.embedDim
        self._freezeBackbone = options.freezeBackbone

        self.register_buffer(
            "_actionRegistry",
            options.actionEmbeddings().detach().to(self._device).clone(),
        )

        keyEmb = options.keyEmbeddings()
        if keyEmb is not None:
            self.register_buffer(
                "_keyRegistry", keyEmb.detach().to(self._device).clone()
            )
        else:
            self.register_buffer(
                "_keyRegistry", torch.empty(0, self._embedDim, device=self._device)
            )

        textEmb = options.textEmbeddings()
        if textEmb is not None:
            self.register_buffer(
                "_textRegistry", textEmb.detach().to(self._device).clone()
            )
        else:
            self.register_buffer(
                "_textRegistry", torch.empty(0, self._embedDim, device=self._device)
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
        self._argKindHead = nn.Sequential(
            nn.Linear(featDim, featDim),
            nn.ReLU(inplace=True),
            nn.Linear(featDim, len(self._argKinds)),
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
        wasTraining = self.training
        try:
            self.eval()
            out = self.forward(imageArray)

            actionScores = self._cosine(out["actionEmbedding"], self._actionRegistry)
            actionIndex = int(torch.argmax(actionScores, dim=-1).reshape(-1)[0].item())
            actionKey = self._actionKeys[actionIndex]

            kindIndex = int(
                torch.argmax(out["argKindLogits"], dim=-1).reshape(-1)[0].item()
            )
            kind = self._argKinds[kindIndex]
            spatial = out["spatial"].reshape(-1, 4)[0].detach().cpu()

            argument = self._buildArgument(
                kind, spatial, out["keyEmbedding"], out["textEmbedding"]
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
            return {"kind": "coordinate", "x": float(spatial[0]), "y": float(spatial[1])}

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
