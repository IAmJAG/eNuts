# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor
from torch.nn import LSTM, Sequential

# ==================================================================================
from .__policyNet import iPolicyNet


# ==================================================================================
@runtime_checkable
class iSymanticPredictor(iPolicyNet, Protocol):
    rnnLayer: LSTM
    projectionHead: Sequential

    def forwardSequence(
        self, frameSequence: Tensor, intentEmbedding: Tensor,
        previousActionEmbedding: Tensor,
    ) -> Tensor: ...

    def addFrame(self, frame: Tensor) -> None: ...
    def reset(self) -> None: ...

    @property
    def frameCount(self) -> int: ...
    def getFrameFeatures(self) -> Tensor: ...
    def actionScores(
        self, predictedActionEmbedding: Tensor, actionRegistryEmbeddings: Tensor
    ) -> Tensor: ...
    def predictAction(
        self, intentEmbedding: Tensor, previousActionEmbedding: Tensor, 
        actionRegistryEmbeddings: Tensor
    ) -> tuple[Tensor, Tensor]: ...
