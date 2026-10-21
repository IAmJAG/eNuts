# ==================================================================================
"""Smoke: Policy constructs, forward shapes, predict contract.

Seeds come from .test fixtures — not from production policy modules.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import torch

# ==================================================================================
from fluxCore.policy import Policy, PolicyOptions, Vocabulary
from fluxCore.utilities import G_DEFAULT_EMBED_DIM

# ==================================================================================
# Fixture seeds (test-owned)
from pathlib import Path
import sys

_TEST_ROOT = Path(__file__).resolve().parents[2]  # .test/
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS  # noqa: E402


# ==================================================================================
def _buildPolicy(device: str = "cpu") -> tuple[Policy, Vocabulary, Vocabulary]:
    actions = Vocabulary(SEED_ACTIONS, dimension=G_DEFAULT_EMBED_DIM)
    argumentKinds = Vocabulary(SEED_ARGUMENT_KINDS, dimension=G_DEFAULT_EMBED_DIM)
    options = PolicyOptions(
        actions=actions,
        argumentKinds=argumentKinds,
        freezeBackbone=True,
    )
    policy = Policy(options, device=device)
    return policy, actions, argumentKinds


def test_forward_shapes() -> None:
    policy, actions, argumentKinds = _buildPolicy()
    # One process: array of images [T, 3, H, W]
    imageArray = torch.rand(4, 3, 224, 224)

    out = policy.forward(imageArray)

    assert set(out.keys()) == {"actions", "argumentKinds", "spatial"}

    # Batch axis present after fuse (single process → B=1)
    assert out["actions"].shape[-1] == actions.dimension
    assert out["argumentKinds"].shape[-1] == argumentKinds.dimension
    assert out["spatial"].shape[-1] == 4
    assert out["actions"].dim() == 2
    assert torch.all(out["spatial"] >= 0) and torch.all(out["spatial"] <= 1)


def test_predict_contract() -> None:
    policy, actions, argumentKinds = _buildPolicy()
    imageArray = torch.rand(4, 3, 224, 224)

    actionKey, argument = policy.predict(imageArray)

    assert isinstance(actionKey, str)
    assert actionKey in actions.labels

    assert isinstance(argument, dict)
    assert "kind" in argument
    assert argument["kind"] in argumentKinds.labels

    kind = argument["kind"]
    if kind == "coordinate":
        assert "x" in argument and "y" in argument
    elif kind == "box":
        assert {"left", "top", "width", "height"} <= set(argument.keys())
    elif kind == "key":
        assert "code" in argument
    elif kind == "text":
        assert "value" in argument


def test_missing_vocabularies_raise() -> None:
    options = PolicyOptions(actions=None, argumentKinds=None)
    try:
        Policy(options, device="cpu")
        raised = False
    except ValueError:
        raised = True
    assert raised
