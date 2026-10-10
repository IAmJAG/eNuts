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
from .__registry import Registry


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
        data = json.load(lFile)

    registry = Registry(lEmbeddingDim=dim)

    isParameterRegistry = data.get("isParameterRegistry", False)
    for entry in data.get("entries", []):
        key = entry["key"]
        description = entry.get("description", "")

        if isParameterRegistry:
            valuePayload = entry.get("value", None)
            if valuePayload is None:
                raise ValueError(
                    f"Parameter entry '{key}' is missing required 'value' field."
                )            
            
            embedding: Tensor = _deterministicEncoder(
                ident=key, dim=dim,
                payload=valuePayload,
            )
            metadata = {"description": description, "value": valuePayload}

        else:
            embedding: Tensor = _deterministicEncoder(
                ident=key, dim=dim
            )
            metadata = {"description": description}

        registry.register(
            key=key,
            embedding=embedding,
            metadata=metadata,
        )

    return registry
