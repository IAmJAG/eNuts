# ==================================================================================
"""Smoke: typed vocabularies + PolicyOptions serialize; DCPolicy from restored options."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import json
from pathlib import Path
import sys

# ==================================================================================
import numpy as np
import torch

# ==================================================================================
from fluxCore.policy import (
    ActionVocabulary,
    ArgumentKindVocabulary,
    C_NONE_ACTION,
    DCPolicy,
    IntentVocabulary,
    PolicyOptions,
)
from fluxCore.policy.vocabulary import ActionLabel, IntentLabel, Label

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS, SEED_INTENTS  # noqa: E402


# ==================================================================================
def test_action_vocabulary_roundtrip() -> None:
    original = ActionVocabulary(SEED_ACTIONS, dimension=64)
    payload = json.loads(json.dumps(original.encode()))
    restored = ActionVocabulary()
    restored.decode(payload)

    assert restored.labels == original.labels
    assert restored.dimension == original.dimension
    for key in original.labels:
        assert key in restored
        assert isinstance(restored[key], (ActionLabel, Label))
    assert torch.allclose(original.toTensor(), restored.toTensor())


def test_intent_vocabulary_roundtrip() -> None:
    original = IntentVocabulary(SEED_INTENTS, dimension=64)
    payload = json.loads(json.dumps(original.encode()))
    restored = IntentVocabulary()
    restored.decode(payload)

    assert restored.labels == original.labels
    for key in original.labels:
        assert isinstance(restored[key], (IntentLabel, Label))
    assert torch.allclose(original.toTensor(), restored.toTensor())


def test_argument_kind_vocabulary_roundtrip() -> None:
    original = ArgumentKindVocabulary(SEED_ARGUMENT_KINDS, dimension=64)
    payload = json.loads(json.dumps(original.encode()))
    restored = ArgumentKindVocabulary()
    restored.decode(payload)

    assert restored.labels == original.labels
    assert torch.allclose(original.toTensor(), restored.toTensor())


def test_policy_options_roundtrip() -> None:
    original = buildOptions(embedDim=64, featureDim=576, stackSize=4)
    payload = json.loads(json.dumps(original.encode()))
    restored = PolicyOptions()
    restored.decode(payload)
    restored.validate()

    assert restored.actions is not None
    assert restored.argumentKinds is not None
    assert restored.intents is not None
    assert restored.actions.labels == original.actions.labels
    assert restored.argumentKinds.labels == original.argumentKinds.labels
    assert restored.intents.labels == original.intents.labels
    assert restored.stackSize == original.stackSize
    assert restored.durationSec == original.durationSec
    assert restored.featureDimension == original.featureDimension
    assert abs(restored.acceptIntervalSec - original.acceptIntervalSec) < 1e-9


def test_policy_from_restored_options_predicts() -> None:
    original = buildOptions(embedDim=64, featureDim=576, stackSize=4)
    payload = json.loads(json.dumps(original.encode()))
    restored = PolicyOptions()
    restored.decode(payload)

    policy = DCPolicy(restored, device="cpu")
    image = np.random.randint(0, 255, (48, 48, 3), dtype=np.uint8)
    actionKey, argument = policy.predict(
        image,
        intent="idle",
        action=C_NONE_ACTION,
        parameters=None,
    )
    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
