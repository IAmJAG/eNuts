# ==================================================================================
"""Test-only builders for policy options / vocabularies."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from fluxCore.policy import (
    C_DEFAULT_DURATION_SEC,
    C_DEFAULT_STACK_SIZE,
    PolicyOptions,
    Vocabulary,
)
from fluxCore.utilities import G_DEFAULT_EMBED_DIM, G_DEFAULT_FEATURE_DIM

# ==================================================================================
from .seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS


# ==================================================================================
def buildOptions(
    *,
    embedDim: int = G_DEFAULT_EMBED_DIM,
    featureDim: int = G_DEFAULT_FEATURE_DIM,
    freezeBackbone: bool = True,
    stackSize: int = C_DEFAULT_STACK_SIZE,
    durationSec: float = C_DEFAULT_DURATION_SEC,
) -> PolicyOptions:
    actions = Vocabulary(SEED_ACTIONS, dimension=embedDim)
    argumentKinds = Vocabulary(SEED_ARGUMENT_KINDS, dimension=embedDim)
    return PolicyOptions(
        actions=actions,
        argumentKinds=argumentKinds,
        featureDim=featureDim,
        freezeBackbone=freezeBackbone,
        stackSize=stackSize,
        durationSec=durationSec,
    )
