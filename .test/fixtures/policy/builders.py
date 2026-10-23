# ==================================================================================
"""Test-only builders for policy options / vocabularies."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from fluxCore.policy import (
    ActionVocabulary,
    ArgumentKindVocabulary,
    C_DEFAULT_DURATION_SEC,
    C_DEFAULT_STACK_SIZE,
    IntentVocabulary,
    PolicyOptions,
)
from fluxCore.utilities import G_DEFAULT_EMBED_DIM, G_DEFAULT_FEATURE_DIM

# ==================================================================================
from .seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS, SEED_INTENTS


# ==================================================================================
def buildOptions(
    *,
    embedDim: int = G_DEFAULT_EMBED_DIM,
    featureDim: int = G_DEFAULT_FEATURE_DIM,
    freezeBackbone: bool = True,
    stackSize: int = C_DEFAULT_STACK_SIZE,
    durationSec: float = C_DEFAULT_DURATION_SEC,
) -> PolicyOptions:
    return PolicyOptions(
        actions=ActionVocabulary(SEED_ACTIONS, dimension=embedDim),
        argumentKinds=ArgumentKindVocabulary(SEED_ARGUMENT_KINDS, dimension=embedDim),
        intents=IntentVocabulary(SEED_INTENTS, dimension=embedDim),
        featureDim=featureDim,
        freezeBackbone=freezeBackbone,
        stackSize=stackSize,
        durationSec=durationSec,
    )
