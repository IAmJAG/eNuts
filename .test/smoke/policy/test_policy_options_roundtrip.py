# ==================================================================================
"""Smoke: PolicyOptions serializes and restores enough to build Policy."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import json
from pathlib import Path
import sys

# ==================================================================================
import torch

# ==================================================================================
from fluxCore.policy import Policy, PolicyOptions, Vocabulary
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

    # JSON boundary
    payload = json.loads(json.dumps(blob))

    restored = Vocabulary()
    restored.decode(payload)

    assert restored.dimension == original.dimension
    assert restored.size == original.size
    assert restored.labels == original.labels
    for key in original.labels:
        assert key in restored
        assert isinstance(restored[key], Label)
        assert restored[key].id == key
        assert restored[key].description == original[key].description

    # Embedding table must match (deterministic from ids + dimension)
    assert torch.allclose(original.toTensor(), restored.toTensor())


def test_policy_options_roundtrip() -> None:
    original = buildOptions(embedDim=64, featureDim=256, freezeBackbone=True)
    blob = original.encode()
    payload = json.loads(json.dumps(blob))

    restored = PolicyOptions()
    restored.decode(payload)

    assert restored.featureDimension == original.featureDimension
    assert restored.freezeBackbone == original.freezeBackbone
    assert restored.actions is not None and restored.argumentKinds is not None
    assert restored.actions.labels == original.actions.labels
    assert restored.argumentKinds.labels == original.argumentKinds.labels
    assert restored.actions.dimension == original.actions.dimension
    assert restored.argumentKinds.dimension == original.argumentKinds.dimension


def test_policy_from_restored_options_predicts() -> None:
    original = buildOptions(embedDim=64, featureDim=256, freezeBackbone=True)
    payload = json.loads(json.dumps(original.encode()))

    restored = PolicyOptions()
    restored.decode(payload)

    policy = Policy(restored, device="cpu")
    imageArray = torch.rand(4, 3, 224, 224)

    actionKey, argument = policy.predict(imageArray)

    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
