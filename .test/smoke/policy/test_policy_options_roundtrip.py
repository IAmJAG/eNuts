# ==================================================================================
"""Smoke: PolicyOptions serializes intents; restored options build DCPolicy."""
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
from fluxCore.policy import C_NONE_ACTION, DCPolicy, PolicyOptions, Vocabulary
from fluxCore.policy.vocabulary import Label

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS, SEED_INTENTS  # noqa: E402


# ==================================================================================
def test_vocabulary_roundtrip() -> None:
    original = Vocabulary(SEED_ACTIONS, dimension=64)
    payload = json.loads(json.dumps(original.encode()))
    restored = Vocabulary()
    restored.decode(payload)
    assert restored.labels == original.labels
    assert torch.allclose(original.toTensor(), restored.toTensor())


def test_policy_options_roundtrip() -> None:
    original = buildOptions(embedDim=64, featureDim=576, stackSize=4)
    payload = json.loads(json.dumps(original.encode()))
    restored = PolicyOptions()
    restored.decode(payload)
    restored.validate()

    assert restored.intents is not None
    assert restored.intents.labels == original.intents.labels
    assert restored.actions.labels == original.actions.labels
    assert restored.stackSize == original.stackSize


def test_policy_from_restored_options_predicts() -> None:
    original = buildOptions(embedDim=64, featureDim=576, stackSize=4)
    payload = json.loads(json.dumps(original.encode()))
    restored = PolicyOptions()
    restored.decode(payload)

    policy = DCPolicy(restored, device="cpu")
    image = np.random.randint(0, 255, (48, 48, 3), dtype=np.uint8)
    actionKey, argument = policy.predict(
        image, intent="idle", action=C_NONE_ACTION, parameters=None
    )
    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
