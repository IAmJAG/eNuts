# ==================================================================================
# src/fluxCore/policies/__semanticPredictor.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from pathlib import Path
from typing import Any

# ==================================================================================
import torch
from torch import Tensor, nn
from torchvision import models

# ==================================================================================
from ...types.interface.policies import iSymanticPredictor

# ==================================================================================
C_DEFAULT_OPTIONS: dict[str, Any] = {
    "FEATURE_DIM": 512,
    "INTENT_EMBEDDING_DIM": 64,
    "ACTION_EMBEDDING_DIM": 64,
    "PARAMETER_EMBEDDING_DIM": 256,
    "HIDDEN_DIM": 256,
    "LAYERS": 2,
    "DROPOUT": 0.2,
    "INTERMEDIATE_HIDDEN_LAYER": 256,
    "TEMPERATURE": 0.07,
    "MAX_SEQUENCE_LENGTH": 16,
    "FREEZE_BACKBONE": True,
}
# ==================================================================================


# ==================================================================================
class SemanticPredictorPolicy(nn.Module, iSymanticPredictor):
    """
    Stateful semantic policy for sequential UI/device automation, supporting
    dual-head prediction for both Actions and Parameters conditioned on Intent,
    initialized with immutable, device-locked registry embedding references.
    """

    CHECKPOINT_VERSION = 3

    def __init__(
        self,
        actionRegistryEmbeddings: Tensor,
        parameterRegistryEmbeddings: Tensor,
        options: dict[str, Any] | None = None,
        device: str | torch.device = "cuda",
    ) -> None:
        super().__init__()

        self._options = {**C_DEFAULT_OPTIONS, **(options or {})}

        # Resolve target device safely
        if isinstance(device, str):
            if device.lower().startswith("cuda") and not torch.cuda.is_available(): device = "cpu"
            self._device = torch.device(device)

        else:
            self._device = device

        # Lock and bind registries immutably to the target device
        self._actionRegistryEmbeddings = (
            actionRegistryEmbeddings.detach().to(self._device).clone()
        )
        self._parameterRegistryEmbeddings = (
            parameterRegistryEmbeddings.detach().to(self._device).clone()
        )

        self._featureDim = int(self._options["FEATURE_DIM"])
        self._intentEmbeddingDim = int(self._options["INTENT_EMBEDDING_DIM"])
        self._actionEmbeddingDim = int(self._options["ACTION_EMBEDDING_DIM"])
        self._parameterEmbeddingDim = int(self._options["PARAMETER_EMBEDDING_DIM"])
        self._hiddenDim = int(self._options["HIDDEN_DIM"])
        self._maxSequenceLength = int(self._options["MAX_SEQUENCE_LENGTH"])
        self._temperature = float(self._options["TEMPERATURE"])
        self._freezeBackbone = bool(self._options["FREEZE_BACKBONE"])

        if self._maxSequenceLength < 1:
            raise ValueError("MAX_SEQUENCE_LENGTH must be >= 1")

        if self._temperature <= 0:
            raise ValueError("TEMPERATURE must be > 0")

        self._initializeMobileNet()

        # Fusion input: Visual features + Intent + Previous Action + Previous Parameter
        fusionDim = (
            self._featureDim
            + self._intentEmbeddingDim
            + self._actionEmbeddingDim
            + self._parameterEmbeddingDim
        )

        self.rnnLayer = nn.LSTM(
            input_size=fusionDim,
            hidden_size=self._hiddenDim,
            num_layers=int(self._options["LAYERS"]),
            batch_first=True,
            dropout=(
                float(self._options["DROPOUT"])
                if int(self._options["LAYERS"]) > 1
                else 0.0
            ),
        )

        # Head A: Projects hidden state to Action Embedding Space
        self.actionProjectionHead = nn.Sequential(
            nn.Linear(self._hiddenDim, int(self._options["INTERMEDIATE_HIDDEN_LAYER"])),
            nn.LayerNorm(int(self._options["INTERMEDIATE_HIDDEN_LAYER"])),
            nn.GELU(),
            nn.Linear(
                int(self._options["INTERMEDIATE_HIDDEN_LAYER"]),
                self._actionEmbeddingDim,
            ),
        )

        # Head B: Projects hidden state to Parameter Embedding Space
        self.parameterProjectionHead = nn.Sequential(
            nn.Linear(self._hiddenDim, int(self._options["INTERMEDIATE_HIDDEN_LAYER"])),
            nn.LayerNorm(int(self._options["INTERMEDIATE_HIDDEN_LAYER"])),
            nn.GELU(),
            nn.Linear(
                int(self._options["INTERMEDIATE_HIDDEN_LAYER"]),
                self._parameterEmbeddingDim,
            ),
        )

        # Runtime-only visual history[cite: 6]
        self._frameFeatures: deque[Tensor] = deque(maxlen=self._maxSequenceLength)
        self._runtimeDevice: torch.device | None = None

        # Move entire model structure to target device
        self.to(self._device)

    # ------------------------------------------------------------------
    # Device helpers
    # ------------------------------------------------------------------
    @property
    def device(self) -> torch.device:
        return self._device

    # ------------------------------------------------------------------
    # Visual encoder
    # ------------------------------------------------------------------
    def _initializeMobileNet(self) -> None:
        weights = models.MobileNet_V3_Small_Weights.DEFAULT
        mobileNet = models.mobilenet_v3_small(weights=weights)

        self._backbone = nn.Sequential(
            mobileNet.features,
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

        self._featureProjection = nn.Sequential(
            nn.Linear(576, self._featureDim),
            nn.LayerNorm(self._featureDim),
            nn.GELU(),
        )

        if self._freezeBackbone:
            for parameter in self._backbone.parameters():
                parameter.requires_grad = False
            self._backbone.eval()

    def train(self, mode: bool = True) -> SemanticPredictorPolicy:
        super().train(mode)
        if self._freezeBackbone:
            self._backbone.eval()
        return self

    def _validateFrames(self, frames: Tensor) -> Tensor:
        if frames.dim() == 3:
            frames = frames.unsqueeze(0)
        if frames.dim() != 4:
            raise ValueError("Frames must have shape [C,H,W] or [B,C,H,W]")
        if frames.shape[1] != 3:
            raise ValueError("Expected 3-channel RGB frames")

        return frames.to(device=self._device, dtype=torch.float32)

    def extractFrameFeatures(self, frame: Tensor) -> Tensor:
        frame = self._validateFrames(frame)
        if self._freezeBackbone:
            with torch.no_grad():
                backboneFeatures = self._backbone(frame)
        else:
            backboneFeatures = self._backbone(frame)

        return self._featureProjection(backboneFeatures)

    def extractSequenceFeatures(self, frameSequence: Tensor) -> Tensor:
        if frameSequence.dim() == 4:
            frameSequence = frameSequence.unsqueeze(0)
        if frameSequence.dim() != 5:
            raise ValueError("frameSequence must have shape [T,C,H,W] or [B,T,C,H,W]")

        batchSize, sequenceLength, channels, height, width = frameSequence.shape
        frames = frameSequence.reshape(
            batchSize * sequenceLength, channels, height, width
        )
        features = self.extractFrameFeatures(frames)
        return features.reshape(batchSize, sequenceLength, self._featureDim)

    # ------------------------------------------------------------------
    # Stateful runtime frame buffer
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self._frameFeatures.clear()
        self._runtimeDevice = None

    def addFrame(self, frame: Tensor) -> None:
        if self.training:
            raise RuntimeError(
                "addFrame() is intended for inference. Use forwardSequence() during training[cite: 6]."
            )

        if frame.dim() == 4:
            if frame.shape[0] != 1:
                raise ValueError("addFrame() accepts one frame at a time[cite: 6]")
        elif frame.dim() != 3:
            raise ValueError("frame must have shape [C,H,W] or [1,C,H,W][cite: 6]")

        with torch.no_grad():
            features = self.extractFrameFeatures(frame)

        features = features.squeeze(0).detach()
        if self._runtimeDevice != features.device:
            self._frameFeatures.clear()
            self._runtimeDevice = features.device

        self._frameFeatures.append(features)

    @property
    def frameCount(self) -> int:
        return len(self._frameFeatures)

    def getFrameFeatures(self) -> Tensor:
        if not self._frameFeatures:
            raise RuntimeError(
                "No frames have been added. Call addFrame() first[cite: 6]."
            )
        return torch.stack(list(self._frameFeatures), dim=0).unsqueeze(0)

    # ------------------------------------------------------------------
    # Embedding validation and fusion
    # ------------------------------------------------------------------
    @staticmethod
    def _prepareEmbedding(
        embedding: Tensor,
        batchSize: int,
        embeddingDim: int,
        name: str,
        device: torch.device,
        dtype: torch.dtype,
    ) -> Tensor:
        if embedding.dim() == 1:
            embedding = embedding.unsqueeze(0)
        if embedding.dim() != 2:
            raise ValueError(f"{name} must have shape [D] or [B,D]")
        if embedding.shape[-1] != embeddingDim:
            raise ValueError(
                f"{name} dimension is {embedding.shape[-1]}; expected {embeddingDim}"
            )
        if embedding.shape[0] == 1 and batchSize > 1:
            embedding = embedding.expand(batchSize, -1)
        if embedding.shape[0] != batchSize:
            raise ValueError(
                f"{name} batch size {embedding.shape[0]} does not match visual batch size {batchSize}"
            )
        return embedding.to(device=device, dtype=dtype)

    def _predictFromFeatures(
        self,
        visualFeatures: Tensor,
        intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
        previousParameterEmbedding: Tensor,
    ) -> tuple[Tensor, Tensor]:
        batchSize, sequenceLength, _ = visualFeatures.shape
        device, dtype = visualFeatures.device, visualFeatures.dtype

        intentEmbedding = self._prepareEmbedding(
            intentEmbedding,
            batchSize,
            self._intentEmbeddingDim,
            "intentEmbedding",
            device,
            dtype,
        )
        previousActionEmbedding = self._prepareEmbedding(
            previousActionEmbedding,
            batchSize,
            self._actionEmbeddingDim,
            "previousActionEmbedding",
            device,
            dtype,
        )
        previousParameterEmbedding = self._prepareEmbedding(
            previousParameterEmbedding,
            batchSize,
            self._parameterEmbeddingDim,
            "previousParameterEmbedding",
            device,
            dtype,
        )

        intentSeq = intentEmbedding.unsqueeze(1).expand(-1, sequenceLength, -1)
        prevActionSeq = previousActionEmbedding.unsqueeze(1).expand(
            -1, sequenceLength, -1
        )
        prevParamSeq = previousParameterEmbedding.unsqueeze(1).expand(
            -1, sequenceLength, -1
        )

        fusedSequence = torch.cat(
            (visualFeatures, intentSeq, prevActionSeq, prevParamSeq),
            dim=-1,
        )

        rnnOutput, _ = self.rnnLayer(fusedSequence)
        finalStepFeatures = rnnOutput[:, -1, :]

        predictedActionEmb = nn.functional.normalize(
            self.actionProjectionHead(finalStepFeatures), p=2, dim=-1
        )
        predictedParamEmb = nn.functional.normalize(
            self.parameterProjectionHead(finalStepFeatures), p=2, dim=-1
        )

        return predictedActionEmb, predictedParamEmb

    # ------------------------------------------------------------------
    # Training & Inference Interfaces
    # ------------------------------------------------------------------
    def forwardSequence(
        self,
        frameSequence: Tensor,
        intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
        previousParameterEmbedding: Tensor,
    ) -> tuple[Tensor, Tensor]:
        visualFeatures = self.extractSequenceFeatures(frameSequence)
        return self._predictFromFeatures(
            visualFeatures,
            intentEmbedding,
            previousActionEmbedding,
            previousParameterEmbedding,
        )

    def forward(
        self,
        intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
        previousParameterEmbedding: Tensor,
    ) -> tuple[Tensor, Tensor]:
        if not self._frameFeatures:
            raise RuntimeError(
                "Visual history is empty. Call addFrame() first[cite: 6]."
            )

        visualFeatures = self.getFrameFeatures()
        return self._predictFromFeatures(
            visualFeatures,
            intentEmbedding,
            previousActionEmbedding,
            previousParameterEmbedding,
        )

    # ------------------------------------------------------------------
    # Registry Scoring (Actions & Parameters)
    # ------------------------------------------------------------------
    def actionScores(self, predictedActionEmbedding: Tensor) -> Tensor:
        predicted = nn.functional.normalize(predictedActionEmbedding, p=2, dim=-1)
        registry = nn.functional.normalize(self._actionRegistryEmbeddings, p=2, dim=-1)
        return torch.matmul(predicted, registry.T) / self._temperature

    def parameterScores(self, predictedParameterEmbedding: Tensor) -> Tensor:
        predicted = nn.functional.normalize(predictedParameterEmbedding, p=2, dim=-1)
        registry = nn.functional.normalize(
            self._parameterRegistryEmbeddings, p=2, dim=-1
        )
        return torch.matmul(predicted, registry.T) / self._temperature

    @torch.no_grad()
    def predictNext(
        self,
        intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
        previousParameterEmbedding: Tensor,
    ) -> tuple[Tensor, Tensor, Tensor, Tensor]:
        wasTraining = self.training
        try:
            self.eval()
            predActionEmb, predParamEmb = self.forward(
                intentEmbedding, previousActionEmbedding, previousParameterEmbedding
            )
            actionScores = self.actionScores(predActionEmb)
            paramScores = self.parameterScores(predParamEmb)
            return predActionEmb, predParamEmb, actionScores, paramScores
        finally:
            if wasTraining:
                self.train()

    # ------------------------------------------------------------------
    # Training Losses
    # ------------------------------------------------------------------
    def registryLoss(
        self,
        predictedActionEmb: Tensor,
        predictedParamEmb: Tensor,
        targetActionIndex: Tensor,
        targetParameterIndex: Tensor,
    ) -> Tensor:
        actionScores = self.actionScores(predictedActionEmb)
        paramScores = self.parameterScores(predictedParamEmb)

        actionLoss = nn.functional.cross_entropy(
            actionScores,
            targetActionIndex.to(device=actionScores.device, dtype=torch.long),
        )
        paramLoss = nn.functional.cross_entropy(
            paramScores,
            targetParameterIndex.to(device=paramScores.device, dtype=torch.long),
        )

        return actionLoss + paramLoss

    # ------------------------------------------------------------------
    # Checkpointing
    # ------------------------------------------------------------------
    def save(
        self, path: str | Path, optimizer: torch.optim.Optimizer | None = None
    ) -> None:
        checkpoint: dict[str, Any] = {
            "version": self.CHECKPOINT_VERSION,
            "model_state": self.state_dict(),
            "options": self._options,
            "action_registry_embeddings": self._actionRegistryEmbeddings,
            "parameter_registry_embeddings": self._parameterRegistryEmbeddings,
        }
        if optimizer is not None:
            checkpoint["optimizer_state"] = optimizer.state_dict()
        torch.save(checkpoint, path)

    @classmethod
    def load(
        cls,
        path: str | Path,
        device: str | torch.device = "cuda",
        optimizer: torch.optim.Optimizer | None = None,
    ) -> tuple[iSymanticPredictor, dict[str, Any]]:
        checkpoint = torch.load(path, map_location=device, weights_only=False)
        if checkpoint.get("version") != cls.CHECKPOINT_VERSION:
            raise ValueError("Unsupported SemanticPredictorPolicy checkpoint version")

        model = cls(
            actionRegistryEmbeddings=checkpoint["action_registry_embeddings"],
            parameterRegistryEmbeddings=checkpoint["parameter_registry_embeddings"],
            options=checkpoint["options"],
            device=device,
        )
        model.load_state_dict(checkpoint["model_state"])

        if optimizer is not None and "optimizer_state" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state"])

        model.reset()
        return model, checkpoint["options"]
