# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, Optional, Tuple, Union

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
from ..utilities import (
    G_DEFAULT_FEATURE_DIM,
    G_FRAME_SIZE,
    G_NORMALIZE_MEAN,
    G_NORMALIZE_STD,
    G_PARAM_DIM,
    getTorchDevice,
)
from .__policyOptions import C_NONE_ACTION, C_NONE_ARGUMENT_KIND, PolicyOptions


# ==================================================================================
class DCPolicy(nn.Module, iPolicy):
    """
    Discrete-Continuous Policy.

    Context (full joint):
      intent  — blanket over the carousel
      slot_t  — (visual_t, action_t, parameters_t)

    Output: next action + argument (kind + spatial / open fields).
    """

    CP_VERSION: str = "2.0"
    def __init__(
        self, options: PolicyOptions, device: Optional[Union[str, TorchDevice]] = "cuda",
        *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        options.validate()

        weights: MobileNetV3 = models.mobilenet_v3_small(
            weights=MobileNet_V3_Small_Weights.DEFAULT
        )

        backbone: nn.Sequential = nn.Sequential(
            weights.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )

        if options.freezeBackbone:
            for param in backbone.parameters():
                param.requires_grad = False

        transform = transforms.Compose(
            [
                transforms.Resize((G_FRAME_SIZE, G_FRAME_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(mean=G_NORMALIZE_MEAN, std=G_NORMALIZE_STD),
            ]
        )

        actionEmbedDim = options.actions.dimension
        argKindEmbedDim = options.argumentKinds.dimension
        intentEmbedDim = options.intents.dimension
        featureDim = options.featureDimension

        slotIn = G_DEFAULT_FEATURE_DIM + actionEmbedDim + G_PARAM_DIM
        self._slotMerge = nn.Sequential(
            nn.Linear(slotIn, featureDim),
            nn.ReLU(inplace=True),
        )
        
        self._contextMerge = nn.Sequential(
            nn.Linear(featureDim + intentEmbedDim, featureDim),
            nn.ReLU(inplace=True),
        )

        self._actionHead = nn.Sequential(
            nn.Linear(featureDim, featureDim),
            nn.ReLU(inplace=True),
            nn.Linear(featureDim, actionEmbedDim),
        )

        self._argumentKindHead = nn.Sequential(
            nn.Linear(featureDim, featureDim),
            nn.ReLU(inplace=True),
            nn.Linear(featureDim, argKindEmbedDim),
        )

        self._spatialHead = nn.Sequential(
            nn.Linear(featureDim, featureDim),
            nn.ReLU(inplace=True),
            nn.Linear(featureDim, 4),
            nn.Sigmoid(),
        )

        device = getTorchDevice(device)

        self._backbone = backbone
        self._transform = transform
        self._device: TorchDevice = device
        self._freezeBB = options.freezeBackbone
        self._stackSize = int(options.stackSize)
        self._acceptIntervalSec = float(options.acceptIntervalSec)
        self._lastAcceptTime: Optional[float] = None

        self._actionVocabulary: iVocabulary = options.actions
        self._argumentKindVocabulary: iVocabulary = options.argumentKinds
        self._intentVocabulary: iVocabulary = options.intents
        self._actionLabels: tuple[str, ...] = tuple(options.actions.labels)
        self._argKindLabels: tuple[str, ...] = tuple(options.argumentKinds.labels)
        self._intentLabels: tuple[str, ...] = tuple(options.intents.labels)

        self._actionIndex: Dict[str, int] = {
            label: i for i, label in enumerate(self._actionLabels)
        }

        self._argKindIndex: Dict[str, int] = {
            label: i for i, label in enumerate(self._argKindLabels)
        }

        self._intentIndex: Dict[str, int] = {
            label: i for i, label in enumerate(self._intentLabels)
        }

        self._actionEmbeddings: Tensor
        self._argKindEmbeddings: Tensor
        self._intentEmbeddings: Tensor

        self.register_buffer(
            "_actionEmbeddings",
            options.actions.toTensor().detach()
            .to(device=device, dtype=torch.float32).clone(),
        )
        self.register_buffer(
            "_argKindEmbeddings",
            options.argumentKinds.toTensor().detach()
            .to(device=device, dtype=torch.float32).clone(),
        )
        self.register_buffer(
            "_intentEmbeddings",
            options.intents.toTensor().detach()
            .to(device=device, dtype=torch.float32).clone(),
        )

        # Carousel of slots: (visual [3,H,W], actionEmb [A], param [P])
        blankVisual = torch.zeros(
            3, G_FRAME_SIZE, G_FRAME_SIZE, dtype=torch.float32, device=device
        )
        noneActionEmb = self._lookupActionEmbedding(C_NONE_ACTION).detach()
        emptyParam = torch.zeros(G_PARAM_DIM, dtype=torch.float32, device=device)
        self._carousel: Deque[Tuple[Tensor, Tensor, Tensor]] = deque(
            [
                (blankVisual.clone(), noneActionEmb.clone(), emptyParam.clone())
                for _ in range(self._stackSize)
            ],
            maxlen=self._stackSize,
        )

        self.to(device=device)

    def _lookupActionEmbedding(self, action: str) -> Tensor:
        idx = self._actionIndex.get(action, self._actionIndex.get(C_NONE_ACTION, 0))
        return self._actionEmbeddings[idx]

    def _lookupIntentEmbedding(self, intent: str) -> Tensor:
        idx = self._intentIndex.get(intent, 0)
        return self._intentEmbeddings[idx]

    def _encodeParameters(self, parameters: Optional[Dict[str, Any]]) -> Tensor:
        """Fixed [C_PARAM_DIM] vector on device. EMPTY → zeros."""
        out = torch.zeros(G_PARAM_DIM, dtype=torch.float32, device=self._device)
        if not parameters:
            return out

        kind = str(parameters.get("kind", C_NONE_ARGUMENT_KIND))
        if kind == "coordinate":
            out[0] = float(parameters.get("x", 0.0))
            out[1] = float(parameters.get("y", 0.0))

        elif kind == "box":
            out[0] = float(parameters.get("left", 0.0))
            out[1] = float(parameters.get("top", 0.0))
            out[2] = float(parameters.get("width", 0.0))
            out[3] = float(parameters.get("height", 0.0))

        elif kind == "key":
            code = str(parameters.get("code", ""))
            out[4] = (hash(code) % 1000) / 1000.0

        elif kind == "text":
            value = str(parameters.get("value", ""))
            out[5] = (hash(value) % 1000) / 1000.0

        kindIdx = self._argKindIndex.get(kind)
        if kindIdx is not None and self._argKindEmbeddings.numel() > 0:
            k = self._argKindEmbeddings[kindIdx][:2]
            out[6] = float(k[0].item()) if k.numel() > 0 else 0.0
            out[7] = float(k[1].item()) if k.numel() > 1 else 0.0

        return out

    def _shouldAccept(self, timestamp: float) -> bool:
        if self._lastAcceptTime is None: return True
        return (float(timestamp) - self._lastAcceptTime) >= self._acceptIntervalSec

    def _toPil(self, image: Any) -> Image.Image:
        if isinstance(image, ndarray):
            if image.dtype != np.uint8: 
                image = np.clip(image, 0, 255).astype(np.uint8)

            return Image.fromarray(image)

        if isinstance(image, Tensor):
            t = image.detach().cpu()
            if t.ndim == 3 and t.shape[0] in (1, 3):
                t = t.permute(1, 2, 0)

            arr = t.numpy()
            if arr.max() <= 1.5:
                arr = (arr * 255).astype(np.uint8)

            else:
                arr = arr.astype(np.uint8)

            return Image.fromarray(arr)
        
        if isinstance(image, Image.Image): return image

        raise TypeError(f"Unable to convert image of type {type(image)} to PIL Image")

    def _push(
        self, image: Image.Image | ndarray | Tensor, action: str,
        parameters: Optional[Dict[str, Any]],
    ) -> None:
        if not isinstance(image, Image.Image): image = self._toPil(image)

        visual: Tensor = self._transform(image)
        visual = visual.to(device=self._device, dtype=torch.float32)
        actionEmb = self._lookupActionEmbedding(action).to(self._device)
        paramVec = self._encodeParameters(parameters)
        self._carousel.append((visual, actionEmb, paramVec))

    def _fuseContext(self, intent: str) -> Tensor:
        visuals = torch.stack([s[0] for s in self._carousel], dim=0)  # [T,3,H,W]
        actionEmbs = torch.stack([s[1] for s in self._carousel], dim=0)  # [T,A]
        params = torch.stack([s[2] for s in self._carousel], dim=0)  # [T,P]

        t = visuals.shape[0]
        flat = visuals  # [T,3,H,W]
        if self._freezeBB:
            with torch.no_grad():
                visualFeat = self._backbone(flat)
        else:
            visualFeat = self._backbone(flat)

        # [T, 576+A+P]
        slotIn = torch.cat([visualFeat, actionEmbs, params], dim=-1)
        slotVec = self._slotMerge(slotIn)  # [T, featureDim]
        pooled = slotVec.mean(dim=0, keepdim=True)  # [1, featureDim]

        intentEmb = self._lookupIntentEmbedding(intent).to(self._device)
        intentEmb = intentEmb.unsqueeze(0)  # [1, I]
        merged = torch.cat([pooled, intentEmb], dim=-1)
        return self._contextMerge(merged)  # [1, featureDim]

    def forward(
        self, image: Image.Image | ndarray | Tensor, intent: str,
        action: str = C_NONE_ACTION, parameters: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None, *args, **kwargs,
    ) -> Dict[str, Tensor]:
        if timestamp is None:
            self._push(image, action, parameters)

        elif self._shouldAccept(float(timestamp)):
            self._push(image, action, parameters)
            self._lastAcceptTime = float(timestamp)

        h = self._fuseContext(intent)
        return {
            "ACTIONS": self._actionHead(h),
            "ARGKINDS": self._argumentKindHead(h),
            "SPATIAL": self._spatialHead(h),
        }

    @torch.no_grad()
    def predict(
        self, image: Image.Image | ndarray | Tensor, intent: str,
        action: str = C_NONE_ACTION, parameters: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None,
        *args, **kwargs,
    ) -> tuple[str, Dict[str, Any]]:
        wasTraining = self.training
        try:
            self.eval()
            out = self.forward(
                image, intent=intent, action=action,
                parameters=parameters, timestamp=timestamp,
            )

            actionScores = self._cosine(out["ACTIONS"], self._actionEmbeddings)
            actionIndex = int(torch.argmax(actionScores, dim=-1).reshape(-1)[0].item())
            actionKey = self._actionLabels[actionIndex]

            argKindScores = self._cosine(out["ARGKINDS"], self._argKindEmbeddings)
            argKindIndex = int(torch.argmax(argKindScores, dim=-1).reshape(-1)[0].item())
            argKind = self._argKindLabels[argKindIndex]

            spatial = out["SPATIAL"].reshape(-1, 4)[0].detach().cpu()
            argument = self._buildArgument(argKind, spatial)
            return actionKey, argument
        
        finally:
            if wasTraining: self.train()

    @staticmethod
    def _cosine(embedding: Tensor, table: Tensor) -> Tensor:
        if table.numel() == 0: return embedding.new_zeros(embedding.size(0), 0)
        table = table.to(device=embedding.device, dtype=embedding.dtype)
        emb = F.normalize(embedding, p=2, dim=-1)
        reg = F.normalize(table, p=2, dim=-1)
        return torch.matmul(emb, reg.T)

    def train(self, mode: bool = True) -> iPolicy:
        super().train(mode)
        if self._freezeBB: self._backbone.eval()
        return self

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

        if kind == C_NONE_ARGUMENT_KIND:
            return {"kind": C_NONE_ARGUMENT_KIND}

        return {"kind": kind}

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "VERSION": self.CP_VERSION,
                "MODELSTATE": self.state_dict()
            }, path
        )

    @classmethod
    def load(
        cls, path: str | Path, options: PolicyOptions,
        device: Optional[Union[str, TorchDevice]] = "cuda",
    ) -> iPolicy:
        model: Dict = torch.load(path, map_location="cpu", weights_only=False)
        if model.get("VERSION", None) != cls.CP_VERSION:
            raise ValueError(
                f"Unsupported policy checkpoint version: {model.get('VERSION')!r}"
            )
        if "MODELSTATE" not in model:
            raise ValueError("Policy checkpoint missing MODELSTATE")
        
        policy = cls(options, device=device)
        policy.load_state_dict(model["MODELSTATE"], strict=True)
        return policy
