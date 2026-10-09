# ==================================================================================
from collections import deque

# ==================================================================================
import torch

# ==================================================================================
from torch import Tensor


# ==================================================================================
class SemanticExperienceBuffer:
    def __init__(self, capacity: int = 1000):
        self._buffer = deque(maxlen=capacity)

    def push(self, 
        frameSequence: Tensor, intentEmbedding: Tensor,
        previousActionEmbedding: Tensor, targetActionEmbedding: Tensor,
        targetActionIndex: Tensor | None = None,
    ) -> None:
        self._buffer.append({
            "frameSequence": frameSequence,
            "intentEmbedding": intentEmbedding,
            "previousActionEmbedding": previousActionEmbedding,
            "targetActionEmbedding": targetActionEmbedding,
            "targetActionIndex": targetActionIndex,
        })

    def sampleBatch(self, batchSize: int) -> dict[str, Tensor]:
        """Samples a batch of experiences for training."""
        import random
        batch = random.sample(self._buffer, min(len(self._buffer), batchSize))
        
        # Collate samples into batched tensors suitable for forwardSequence()
        return {
            "frameSequence": torch.stack([s["frameSequence"] for s in batch]),
            "intentEmbedding": torch.stack([s["intentEmbedding"] for s in batch]),
            "previousActionEmbedding": torch.stack([s["previousActionEmbedding"] for s in batch]),
            "targetActionEmbedding": torch.stack([s["targetActionEmbedding"] for s in batch]),
            "targetActionIndex": torch.stack([s["targetActionIndex"] for s in batch]) if batch[0]["targetActionIndex"] is not None else None,
        }

    def __len__(self) -> int:
        return len(self._buffer)