# ==================================================================================
import hashlib
import json

# ==================================================================================
from pathlib import Path
from typing import Any

# ==================================================================================
from torch import Generator, Tensor, randn
from torch.nn import functional as F

# ==================================================================================
from .registry.__registry import Registry


# ==================================================================================
def _deterministicEncoder(ident: str, dim: int, payload: Any = None) -> Tensor:
    lCombinedString: str
    if payload is not None:
        lPayloadString = json.dumps(payload, sort_keys=True)
        lCombinedString = f"{ident}:{lPayloadString}"

    else:
        lCombinedString = ident

    lHashBytes = hashlib.sha256(lCombinedString.encode("utf-8")).digest()
    lSeedInt = int.from_bytes(lHashBytes[:8], byteorder="big")

    lGenerator = Generator()
    lGenerator.manual_seed(lSeedInt)

    lVector = randn(dim, generator=lGenerator)
    return F.normalize(lVector, dim=0)

# ==================================================================================
def loadRegistryFromJson(filePath: str | Path, dim: int) -> Registry:
    lPath = Path(filePath)

    if not lPath.exists():
        raise FileNotFoundError(f"Registry configuration file not found: {lPath}")

    with open(lPath, "r", encoding="utf-8") as lFile:
        lData = json.load(lFile)

    registry = Registry(lEmbeddingDim=dim)

    for lEntry in lData.get("items", []):
        lKey = lEntry["key"]
        lDescription = lEntry.get("description", "")

        if lIsParameterRegistry:
            lValuePayload = lEntry.get("value")
            if lValuePayload is None:
                raise ValueError(
                    f"Parameter entry '{lKey}' is missing required 'value' field."
                )
            lEmbedding = _deterministicEncoder(
                lIdentifier=lKey,
                lEmbeddingDim=lEmbeddingDim,
                lValuePayload=lValuePayload,
            )
            lMetadata = {"description": lDescription, "value": lValuePayload}
        else:
            # Intents and Actions depend strictly on their immutable key string
            lEmbedding = _deterministicEncoder(
                lIdentifier=lKey, lEmbeddingDim=lEmbeddingDim
            )
            lMetadata = {"description": lDescription}

        lRegistry.register(
            lKey=lKey,
            lEmbedding=lEmbedding,
            lMetadata=lMetadata,
        )

    return lRegistry
