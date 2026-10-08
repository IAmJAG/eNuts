# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from torch.nn import LSTM, Sequential

# ==================================================================================
from .__policyNet import iPolicyNet


# ==================================================================================
@runtime_checkable
class iSymanticPredictor(iPolicyNet, Protocol):
    @property
    def featureDim(self) -> int: ...
    
    @property
    def fusionDim(self) -> int: ...

    def projectionHead(self) -> Sequential: ...
    def rnnLayer(self) -> LSTM: ...