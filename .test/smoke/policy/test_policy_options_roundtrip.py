# ==================================================================================
"""Smoke: PolicyOptions serializes; restored options build DCPolicy."""
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
from fluxCore.policy import DCPolicy, PolicyOptions, Vocabulary
from fluxCore.policy.vocabulary import Label

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS  # noqa: E402


# ==================================================================================
def test_vocabulary_roundtrip() -> None:
    original = Vocabulary(SEED_ACTIONS, dimension=64)
    blob = original.encode()
    payload = json.loads(json.dumps(blob))

    restored = Vocabulary()
    restored.decode(payload)

    assert restored.dimension == original.dimension
    assert restored.size == original.size
    assert restored.labels == original.labels
    for key in original.labels:
        assert isinstance(restored[key], Label)
        assert restored[key].description == original[key].description
    assert torch.allclose(original.toTensor(), restored.toTensor())


def test_policy_options_roundtrip() -> None:
    original = buildOptions(embedDim=64, featureDim=576, freezeBackbone=True, stackSize=4)
    payload = json.loads(json.dumps(original.encode()))

    restored = PolicyOptions()
    restored.decode(payload)
    restored.validate()

    assert restored.featureDimension == original.featureDimension
    assert restored.freezeBackbone == original.freezeBackbone
    assert restored.stackSize == original.stackSize
    assert restored.durationSec == original.durationSec
    assert restored.actions.labels == original.actions.labels
    assert restored.argumentKinds.labels == original.argumentKinds.labels


def test_policy_from_restored_options_predicts() -> None:
    original = buildOptions(embedDim=64, featureDim=576, freezeBackbone=True, stackSize=4)
    payload = json.loads(json.dumps(original.encode()))

    restored = PolicyOptions()
    restored.decode(payload)

    policy = DCPolicy(restored, device="cpu")
    image = np.random.randint(0, 255, (48, 48, 3), dtype=np.uint8)
    actionKey, argument = policy.predict(image)

    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
