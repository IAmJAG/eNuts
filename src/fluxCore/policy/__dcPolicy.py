# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, Optional, Union

# ==================================================================================
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ==================================================================================
from numpy import ndarray
from PIL import Image
from torch import Tensor
from torch import device as TorchDevice
from torchvision import models, transforms
from torchvision.models import MobileNet_V3_Small_Weights, MobileNetV3

# ==================================================================================
from ..types.interface.policy import iPolicy
from ..types.interface.policy.vocabulary import iVocabulary
from ..utilities import G_NORMALIZE_MEAN, G_NORMALIZE_STD, getTorchDevice
from .__policyOptions import PolicyOptions


# ==================================================================================
class DCPolicy(nn.Module, iPolicy):
    """
    Descrete-Continuous Policy
    """
    CP_VERSION: str = "1.0"
    def __init__(
        self, options: PolicyOptions,
        device: Optional[Union[str, TorchDevice]] = "cuda", 
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        weights: MobileNetV3 = models.mobilenet_v3_small(
            weights=MobileNet_V3_Small_Weights.DEFAULT
        )

        backbone: nn.Sequential = nn.Sequential(
            weights.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )

        transform = self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=G_NORMALIZE_MEAN,
                    std=G_NORMALIZE_STD,
                ),
                
            ]
        )

        if options.freezeBackbone:
            for param in backbone.parameters():
                param.requires_grad = False

        actionEmbeddingDimension = options.actions.dimension
        argKindEmbeddingDimension = options.argumentKinds.dimension

        featureDimension = options.featureDimension
        
        # region: HEADS
        self._actionHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, actionEmbeddingDimension),
        )

        self._argumentKindHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, argKindEmbeddingDimension),
        )

        self._spatialHead = nn.Sequential(
            nn.Linear(featureDimension, featureDimension),
            nn.ReLU(inplace=True),
            nn.Linear(featureDimension, 4),
            nn.Sigmoid(),
        )
        # endregion

        device = getTorchDevice(device)        

        self._backbone = backbone
        self._transform = transform
        self._device: TorchDevice = device
        self._freezeBB: bool = options.freezeBackbone

        self._actionVocabulary: iVocabulary = options.actions
        self._argumentKindVocabulary: iVocabulary = options.argumentKinds
        self._actionLabels: tuple[str, ...] = tuple(options.actions.labels)
        self._argKindLabels: tuple[str, ...] = tuple(options.argumentKinds.labels)

        self._actionEmbeddings: Tensor
        self._argKindEmbeddings: Tensor

        self.register_buffer(
            "_actionEmbeddings",
            options.actions.toTensor()
            .detach()
            .to(device=self._device, dtype=torch.float32)
            .clone(),
        )

        self.register_buffer(
            "_argKindEmbeddings",
            options.argumentKinds.toTensor()
            .detach()
            .to(device=self._device, dtype=torch.float32)
            .clone(),
        )

        self._imageCarousel: Deque[Tensor] = deque[Tensor](maxlen=options.stackSize)

        self.to(device=device)

    def _push(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            image = self._toPil(image)

        image: Tensor = self._transform(image)
        image = image.to(device=self._device, dtype=torch.float32)
        self._imageCarousel.append(image)

    def _toPil(self, image):
        if isinstance(image, ndarray):
            if image.dtype != np.uint8: 
                image = np.clip(image, 0, 255).astype(np.uint8)

            return Image.fromarray(image)
        
        if isinstance(image, Tensor):
            t = image.detach().cpu()
            if t.ndim == 3 and t.shape[0] in (1, 3):  # CHW
                t = t.permute(1, 2, 0)
            arr = t.numpy()
            if arr.max() <= 1.5:
                arr = (arr * 255).astype(np.uint8)
            else:
                arr = arr.astype(np.uint8)
            return Image.fromarray(arr)

        if isinstance(image, Image.Image):
            return image
        
        raise TypeError(f"Unable to convert image of type {type(image)} to PIL Image")

    def forward(self, image: Image.Image, *args, **kwargs) -> dict[str, Tensor]:
        self._push(image)

        carousel: Deque[Tensor] = self._imageCarousel
        actionHead: nn.Module = self._actionHead
        argKindHead: nn.Module = self._argumentKindHead
        spatialHead: nn.Module = self._spatialHead

        finalFeatures = self._fuse(carousel)
        return {
            "ACTIONS": actionHead(finalFeatures),
            "ARGKINDS": argKindHead(finalFeatures),
            "SPATIAL": spatialHead(finalFeatures),
        }

    @torch.no_grad()
    def predict(self, image: Image.Image, *args, **kwargs) -> tuple[str, Dict[str, Any]]:
        wasTraining = self.training
        try:
            self.eval()
            out = self.forward(image)

            actionScores = self._cosine(out["ACTIONS"], self._actionEmbeddings)
            actionIndex = int(torch.argmax(actionScores, dim=-1).reshape(-1)[0].item())
            actionKey = self._actionLabels[actionIndex]

            argKindScores = self._cosine(out["ARGKINDS"], self._argKindEmbeddings)
            argKindIndex = int(torch.argmax(argKindScores, dim=-1).reshape(-1)[0].item())
            argKind = self._argKindLabels[argKindIndex]

            spatial = out["SPATIAL"].reshape(-1, 4)[0].detach().cpu()
            argument = self._buildArgument(argKind, spatial)
            return actionKey, argument

        except Exception as e:
            raise e

        finally:
            if wasTraining:
                self.train()

    @staticmethod
    def _cosine(embedding: Tensor, table: Tensor) -> Tensor:
        if table.numel() == 0:
            return embedding.new_zeros(embedding.size(0), 0)
        
        # Always score on the embedding's device (policy _device)
        table = table.to(device=embedding.device, dtype=embedding.dtype)
        emb = F.normalize(embedding, p=2, dim=-1)
        reg = F.normalize(table, p=2, dim=-1)
        return torch.matmul(emb, reg.T)

    def train(self, mode: bool = True) -> iPolicy:
        super().train(mode)
        if self._freezeBB:
            self._backbone.eval()

        return self

    def _fuse(self, frameDeque: Deque[Tensor]) -> Tensor:
        frameSequence = torch.stack(list(frameDeque), dim=0).unsqueeze(0)
        b, t, c, h, w = frameSequence.shape
        flattenedSequence = frameSequence.view(b * t, c, h, w)        
        visualFeatures = self._backbone(flattenedSequence)
        visualSequence = visualFeatures.view(b, t, -1)
        return visualSequence.mean(dim=1)

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
            return {"kind": "key", "code": ""}
        
        if kind == "text":
            return {"kind": "text", "value": ""}
        
        return {"kind": kind}
    
    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "VERSION": self.CP_VERSION,
            "MODELSTATE": self.state_dict(),
        }
        torch.save(checkpoint, path)
    
    @classmethod
    def load(
        cls, path: str | Path, options: PolicyOptions,
        device: Optional[Union[str, TorchDevice]] = "cuda",
    ) -> iPolicy:        
        model = torch.load(path, map_location="cpu", weights_only=False)
        if model.get("VERSION", None) != cls.CP_VERSION:
            raise ValueError(
                f"Unsupported policy checkpoint version: {model.get('VERSION')!r}"
            )

        if "MODELSTATE" not in model:
            raise ValueError("Policy checkpoint missing modelState")

        policy = cls(options, device=device)
        policy.load_state_dict(model["MODELSTATE"], strict=True)
        return policy