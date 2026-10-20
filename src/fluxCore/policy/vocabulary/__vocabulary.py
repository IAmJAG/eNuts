# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List, Union

# ==================================================================================
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel
from .__label import Label


# ==================================================================================
class iVocabulary(Serializable, Dict[str, iLabel]):
    def __init__(self, vocab: Dict[str, Union[iLabel | str]]) -> None: 
        vocab = {k: Label(k, v) if isinstance(v, str) else v for k, v in vocab.items()} 
        super().__init__(vocab)

    @property
    def dimension(self) -> int: 
        return len(self)
    
    @property
    def labels(self) -> List[str]:
        return list(self.keys())

    def toTensor(self) -> Tensor: ...

    
