# ==================================================================================
from __future__ import annotations

# ==================================================================================
import hashlib
from typing import Optional, Sequence

# ==================================================================================
import torch
import torch.nn.functional as F
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
class EmbeddingItem (Serializable):
    def __init__(self, embedding: Tensor, mask: Optional[Sequence[bool]] = None) -> None: