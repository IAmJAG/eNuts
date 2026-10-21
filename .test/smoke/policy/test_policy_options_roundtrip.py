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
    trace("test_vocabulary_roundtrip: build original Vocabulary")
    original = Vocabulary(SEED_ACTIONS, dimension=64)
    trace(f"  labels={original.labels} dimension={original.dimension} size={original.size}")

    blob = original.encode()
    trace(f"  encode keys={list(blob.keys())} type={blob.get('__type__')}")
    trace(f"  encode entries sample={list(blob.get('entries', {}).items())[:1]}")

    payload = json.loads(json.dumps(blob))
    trace("  json boundary ok")

    restored = Vocabulary()
    trace("  decoding into empty Vocabulary")
    restored.decode(payload)
    trace(
        f"  restored labels={restored.labels} dimension={restored.dimension} size={restored.size}"
    )

    assert restored.dimension == original.dimension
    assert restored.size == original.size
    assert restored.labels == original.labels
    for key in original.labels:
        assert key in restored
        assert isinstance(restored[key], Label)
        assert restored[key].id == key
        assert restored[key].description == original[key].description

    assert torch.allclose(original.toTensor(), restored.toTensor())
    trace("test_vocabulary_roundtrip: PASS")


def test_policy_options_roundtrip() -> None:
    trace("test_policy_options_roundtrip: buildOptions")
    original = buildOptions(embedDim=64, featureDim=256, freezeBackbone=True)
    blob = original.encode()
    trace(f"  encode keys={list(blob.keys())} type={blob.get('__type__')}")
    if isinstance(blob.get("actions"), dict):
        trace(f"  actions.__type__={blob['actions'].get('__type__)}")
        trace(f"  actions.entries keys={list(blob['actions'].get('entries', {}).keys())}")

    payload = json.loads(json.dumps(blob))
    restored = PolicyOptions()
    trace("  decoding PolicyOptions")
    restored.decode(payload)
    trace(
        f"  restored featureDimension={restored.featureDimension} "
        f"freezeBackbone={restored.freezeBackbone}"
    )

    assert restored.featureDimension == original.featureDimension
    assert restored.freezeBackbone == original.freezeBackbone
    assert restored.actions is not None and restored.argumentKinds is not None
    assert restored.actions.labels == original.actions.labels
    assert restored.argumentKinds.labels == original.argumentKinds.labels
    assert restored.actions.dimension == original.actions.dimension
    assert restored.argumentKinds.dimension == original.argumentKinds.dimension
    trace("test_policy_options_roundtrip: PASS")


def test_policy_from_restored_options_predicts() -> None:
    trace("test_policy_from_restored_options_predicts: encode/decode options")
    original = buildOptions(embedDim=64, featureDim=256, freezeBackbone=True)
    payload = json.loads(json.dumps(original.encode()))

    restored = PolicyOptions()
    restored.decode(payload)
    trace(
        f"  restored actions={restored.actions.labels if restored.actions else None} "
        f"kinds={restored.argumentKinds.labels if restored.argumentKinds else None}"
    )

    policy = Policy(restored, device="cpu")
    imageArray = torch.rand(4, 3, 224, 224)
    actionKey, argument = policy.predict(imageArray)
    trace(f"  predict actionKey={actionKey!r} argument={argument!r}")

    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
    trace("test_policy_from_restored_options_predicts: PASS")
