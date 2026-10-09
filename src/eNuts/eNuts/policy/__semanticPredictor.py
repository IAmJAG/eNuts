# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from pathlib import Path
from typing import Any

# ==================================================================================
import torch

# ==================================================================================
from torch import Tensor, nn
from torchvision import models

# ==================================================================================
from ...types.interface.policies import iSymanticPredictor

# ==================================================================================
DEFAULT_OPTIONS: dict[str, Any] = {
    "FEATURE_DIM": 512,
    "INTENT_EMBEDDING_DIM": 128,
    "ACTION_EMBEDDING_DIM": 128,
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
    Stateful semantic policy for sequential UI/device automation.

    Runtime interface:
        policy.reset()
        policy.addFrame(frame)
        predictedEmbedding = policy(intentEmbedding, previousActionEmbedding)
        scores = policy.actionScores(predictedEmbedding, actionRegistryEmbeddings)

    Training interface:
        predictedEmbedding = policy.forwardSequence(
            frameSequence,
            intentEmbedding,
            previousActionEmbedding,
        )
    Input frames are expected to be RGB float tensors in [0, 1],
    normalized using the preprocessing associated with the pretrained
    MobileNetV3-Small weights.

    The runtime frame buffer is transient and is not saved in state_dict.
    """

    CHECKPOINT_VERSION = 1
    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__()

        self.options = {**DEFAULT_OPTIONS, **(options or {})}

        self._featureDim = int(self.options["FEATURE_DIM"])
        self._intentEmbeddingDim = int(self.options["INTENT_EMBEDDING_DIM"])
        self._actionEmbeddingDim = int(self.options["ACTION_EMBEDDING_DIM"])
        self._hiddenDim = int(self.options["HIDDEN_DIM"])
        self._maxSequenceLength = int(self.options["MAX_SEQUENCE_LENGTH"])
        self._temperature = float(self.options["TEMPERATURE"])
        self._freezeBackbone = bool(self.options["FREEZE_BACKBONE"])

        if self._maxSequenceLength < 1:
            raise ValueError("MAX_SEQUENCE_LENGTH must be >= 1")

        if self._temperature <= 0:
            raise ValueError("TEMPERATURE must be > 0")

        self._initializeMobileNet()

        fusionDim = (self._featureDim + self._intentEmbeddingDim + self._actionEmbeddingDim)

        self.rnnLayer = nn.LSTM(
            input_size=fusionDim,
            hidden_size=self._hiddenDim,
            num_layers=int(self.options["LAYERS"]),
            batch_first=True,
            dropout=(
                float(self.options["DROPOUT"])
                if int(self.options["LAYERS"]) > 1
                else 0.0
            ),
        )

        self.projectionHead = nn.Sequential(
            nn.Linear(
                self._hiddenDim,
                int(self.options["INTERMEDIATE_HIDDEN_LAYER"]),
            ),
            nn.LayerNorm(int(self.options["INTERMEDIATE_HIDDEN_LAYER"])),
            nn.GELU(),
            nn.Linear(
                int(self.options["INTERMEDIATE_HIDDEN_LAYER"]),
                self._actionEmbeddingDim,
            ),
        )

        # Runtime-only visual history. Each item is one frame feature:
        # [FEATURE_DIM].
        self._frameFeatures: deque[Tensor] = deque(maxlen=self._maxSequenceLength)

        # Cached hidden state is reserved for possible incremental
        # inference. This implementation recomputes the LSTM over the
        # bounded feature window, so no hidden state is retained.
        self._runtimeDevice: torch.device | None = None

    # ------------------------------------------------------------------
    # Device helpers
    # ------------------------------------------------------------------
    @property
    def device(self) -> torch.device:
        return next(self.parameters()).device

    # ------------------------------------------------------------------
    # Visual encoder
    # ------------------------------------------------------------------
    def _initializeMobileNet(self) -> None:
        weights = models.MobileNet_V3_Small_Weights.DEFAULT

        mobileNet = models.mobilenet_v3_small(
            weights=weights,
        )

        self._backbone = nn.Sequential(
            mobileNet.features,
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

        # This projection remains trainable even if the backbone is frozen.
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

        # Prevent frozen backbone BatchNorm statistics from changing.
        if self._freezeBackbone:
            self._backbone.eval()

        return self

    def _validateFrames(self, frames: Tensor) -> Tensor:
        """
        Validate and move frames to the model's device/dtype.
        Accepts: [C,H,W], [B,C,H,W]
        """
        if frames.dim() == 3: frames = frames.unsqueeze(0)

        if frames.dim() != 4: raise ValueError("Frames must have shape [C,H,W] or [B,C,H,W]")

        if frames.shape[1] != 3: raise ValueError("Expected 3-channel RGB frames")

        parameter = next(self._backbone.parameters())
        return frames.to(
            device=parameter.device,
            dtype=parameter.dtype,
        )

    def extractFrameFeatures(self, frame: Tensor) -> Tensor:
        """
        Extract features from one frame or a batch of frames.
        Input:
            [C,H,W] or [B,C,H,W]
        Output:
            [B,FEATURE_DIM]
        """
        frame = self._validateFrames(frame)

        if self._freezeBackbone:
            with torch.no_grad():
                backboneFeatures = self._backbone(frame)

        else:
            backboneFeatures = self._backbone(frame)

        # Intentionally outside no_grad(): the projection can learn
        # while the pretrained backbone remains frozen.
        return self._featureProjection(backboneFeatures)

    def extractSequenceFeatures(self, frameSequence: Tensor) -> Tensor:
        """
        Extract features for a complete sequence.

        Input:
            [T,C,H,W] or [B,T,C,H,W]

        Output:
            [B,T,FEATURE_DIM]
        """
        if frameSequence.dim() == 4:
            frameSequence = frameSequence.unsqueeze(0)

        if frameSequence.dim() != 5:
            raise ValueError("frameSequence must have shape [T,C,H,W] or [B,T,C,H,W]")

        batchSize, sequenceLength, channels, height, width = frameSequence.shape

        frames = frameSequence.reshape(
            batchSize * sequenceLength,
            channels,
            height,
            width,
        )

        features = self.extractFrameFeatures(frames)

        return features.reshape(
            batchSize,
            sequenceLength,
            self._featureDim,
        )

    # ------------------------------------------------------------------
    # Stateful runtime frame buffer
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """
        Clear the current visual history.
        Call this when starting a new episode or situation.
        """
        self._frameFeatures.clear()
        self._runtimeDevice = None

    def addFrame(self, frame: Tensor) -> None:
        """
        Encode and append one frame to the current visual history.

        Older frames are automatically discarded when the rolling
        window reaches MAX_SEQUENCE_LENGTH.

        This is an inference/runtime method. For training, use
        forwardSequence() so gradients can flow through the encoder.
        """
        if self.training:
            raise RuntimeError(
                "addFrame() is intended for inference. "
                "Use forwardSequence() during training."
            )

        if frame.dim() == 4:
            if frame.shape[0] != 1:
                raise ValueError("addFrame() accepts one frame at a time")
            
        elif frame.dim() != 3:
            raise ValueError("frame must have shape [C,H,W] or [1,C,H,W]")

        with torch.no_grad():
            features = self.extractFrameFeatures(frame)

        # Store one feature vector per frame, not the original image.
        features = features.squeeze(0).detach()

        if self._runtimeDevice != features.device:
            self._frameFeatures.clear()
            self._runtimeDevice = features.device

        self._frameFeatures.append(features)

    @property
    def frameCount(self) -> int:
        """Number of frames currently retained."""
        return len(self._frameFeatures)

    def getFrameFeatures(self) -> Tensor:
        """
        Return the retained sequence as [1,T,FEATURE_DIM].
        """
        if not self._frameFeatures:
            raise RuntimeError("No frames have been added. Call addFrame() first.")

        return torch.stack(
            list(self._frameFeatures),
            dim=0,
        ).unsqueeze(0)

    # ------------------------------------------------------------------
    # Embedding validation and fusion
    # ------------------------------------------------------------------

    @staticmethod
    def _prepareEmbedding(
        embedding: Tensor, batchSize: int, embeddingDim: int, name: str,
        device: torch.device, dtype: torch.dtype,
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
                f"{name} batch size {embedding.shape[0]} does not "
                f"match visual batch size {batchSize}"
            )

        return embedding.to(device=device, dtype=dtype)

    def _predictFromFeatures(
        self,
        visualFeatures: Tensor, intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
    ) -> Tensor:
        """
        Shared policy computation.

        visualFeatures:          [B,T,FEATURE_DIM]
        intentEmbedding:         [D_intent] or [B,D_intent]
        previousActionEmbedding: [D_action] or [B,D_action]

        Returns:
            [B,ACTION_EMBEDDING_DIM]
        """
        batchSize, sequenceLength, _ = visualFeatures.shape

        intentEmbedding = self._prepareEmbedding(
            intentEmbedding,
            batchSize,
            self._intentEmbeddingDim,
            "intentEmbedding",
            visualFeatures.device,
            visualFeatures.dtype,
        )

        previousActionEmbedding = self._prepareEmbedding(
            previousActionEmbedding,
            batchSize,
            self._actionEmbeddingDim,
            "previousActionEmbedding",
            visualFeatures.device,
            visualFeatures.dtype,
        )

        intentSequence = intentEmbedding.unsqueeze(1).expand(-1, sequenceLength, -1)

        previousActionSequence = previousActionEmbedding.unsqueeze(1).expand(
            -1, sequenceLength, -1
        )

        fusedSequence = torch.cat(
            (
                visualFeatures,
                intentSequence,
                previousActionSequence,
            ),
            dim=-1,
        )

        rnnOutput, _ = self.rnnLayer(fusedSequence)

        finalStepFeatures = rnnOutput[:, -1, :]

        predictedEmbedding = self.projectionHead(finalStepFeatures)

        return nn.functional.normalize(
            predictedEmbedding,
            p=2,
            dim=-1,
        )

    # ------------------------------------------------------------------
    # Training interface
    # ------------------------------------------------------------------

    def forwardSequence(
        self,
        frameSequence: Tensor, intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
    ) -> Tensor:
        """
        Predict from an explicit sequence of frames.

        Use this method for offline training with video clips,
        annotated image sequences, or replay-buffer samples.

        Input:
            frameSequence: [T,C,H,W] or [B,T,C,H,W]
        Output:
            [B,ACTION_EMBEDDING_DIM]
        """
        visualFeatures = self.extractSequenceFeatures(frameSequence)

        return self._predictFromFeatures(
            visualFeatures,
            intentEmbedding,
            previousActionEmbedding,
        )

    # ------------------------------------------------------------------
    # Runtime inference interface
    # ------------------------------------------------------------------
    def forward(
        self, intentEmbedding: Tensor,previousActionEmbedding: Tensor,
    ) -> Tensor:
        """
        Predict from the visual history already accumulated with
        addFrame().

        No image sequence needs to be passed at each prediction step.
        """
        if not self._frameFeatures:
            raise RuntimeError("Visual history is empty. Call addFrame() first.")

        visualFeatures = self.getFrameFeatures()

        return self._predictFromFeatures(
            visualFeatures,
            intentEmbedding,
            previousActionEmbedding,
        )

    # ------------------------------------------------------------------
    # Action registry scoring
    # ------------------------------------------------------------------
    def actionScores(
        self, predictedActionEmbedding: Tensor, actionRegistryEmbeddings: Tensor
    ) -> Tensor:
        """
        Rank registered actions using cosine similarity.

        predictedActionEmbedding: [B,ACTION_EMBEDDING_DIM]
        actionRegistryEmbeddings: [N,ACTION_EMBEDDING_DIM]

        Returns:
            [B,N] scores
        """
        if actionRegistryEmbeddings.dim() != 2:
            raise ValueError("actionRegistryEmbeddings must have shape [N,D]")

        if actionRegistryEmbeddings.shape[-1] != (self._actionEmbeddingDim):
            raise ValueError("Action registry embedding dimension mismatch")

        predicted = nn.functional.normalize(
            predictedActionEmbedding,
            p=2,
            dim=-1,
        )

        registry = nn.functional.normalize(
            actionRegistryEmbeddings.to(
                device=predicted.device,
                dtype=predicted.dtype,
            ),
            p=2,
            dim=-1,
        )

        return (
            torch.matmul(
                predicted,
                registry.T,
            )
            / self._temperature
        )

    @torch.no_grad()
    def predictAction(
        self,
        intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
        actionRegistryEmbeddings: Tensor,
    ) -> tuple[Tensor, Tensor]:
        """
        Run inference on the currently accumulated frame history.

        Returns:
            predictedEmbedding: [1,ACTION_EMBEDDING_DIM]
            scores:             [1,N]
        """
        wasTraining = self.training

        try:
            self.eval()

            predictedEmbedding = self.forward(
                intentEmbedding,
                previousActionEmbedding,
            )

            scores = self.actionScores(
                predictedEmbedding,
                actionRegistryEmbeddings,
            )

            return predictedEmbedding, scores

        finally:
            if wasTraining:
                self.train()

    # ------------------------------------------------------------------
    # Training losses
    # ------------------------------------------------------------------

    @staticmethod
    def embeddingLoss(
        predictedEmbedding: Tensor,
        targetActionEmbedding: Tensor,
    ) -> Tensor:
        """Cosine-distance loss against the target action embedding."""
        predicted = nn.functional.normalize(
            predictedEmbedding,
            p=2,
            dim=-1,
        )

        target = nn.functional.normalize(
            targetActionEmbedding.to(
                device=predicted.device,
                dtype=predicted.dtype,
            ),
            p=2,
            dim=-1,
        )

        return (
            1.0
            - nn.functional.cosine_similarity(
                predicted,
                target,
                dim=-1,
            )
        ).mean()

    def registryLoss(
        self,
        predictedEmbedding: Tensor,
        actionRegistryEmbeddings: Tensor,
        targetActionIndex: Tensor,
    ) -> Tensor:
        """Cross-entropy loss when each sample has one target action."""
        scores = self.actionScores(
            predictedEmbedding,
            actionRegistryEmbeddings,
        )

        return nn.functional.cross_entropy(
            scores,
            targetActionIndex.to(
                device=scores.device,
                dtype=torch.long,
            ),
        )

    # ------------------------------------------------------------------
    # Checkpointing
    # ------------------------------------------------------------------

    def save(
        self, path: str | Path, 
        optimizer: torch.optim.Optimizer | None = None
    ) -> None:
        
        checkpoint: dict[str, Any] = {
            "version": self.CHECKPOINT_VERSION,
            "model_state": self.state_dict(),
            "options": self.options,
        }

        if optimizer is not None:
            checkpoint["optimizer_state"] = optimizer.state_dict()            

        torch.save(checkpoint, path)

    @classmethod
    def load(
        cls, path: str | Path,
        device: str | torch.device = "CUDA",
        optimizer: torch.optim.Optimizer | None = None,
    ) -> tuple[iSymanticPredictor, dict[str, Any]]:
        checkpoint = torch.load(
            path,
            map_location=device,
            weights_only=False,
        )

        if checkpoint.get("version") != cls.CHECKPOINT_VERSION:
            raise ValueError("Unsupported SemanticPredictorPolicy checkpoint version")

        model = cls(options=checkpoint["options"],)
        model.load_state_dict(checkpoint["model_state"])

        model.to(device)

        if optimizer is not None and "optimizer_state" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state"])

        model.reset()
        return model
