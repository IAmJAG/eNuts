# ==================================================================================
"""Smoke: DCPolicy full context — intent, action, parameters, stride."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
import sys

# ==================================================================================
import numpy as np
import torch

# ==================================================================================
from fluxCore.policy import C_NONE_ACTION, DCPolicy, PolicyOptions
from fluxCore.utilities import G_DEFAULT_EMBED_DIM, G_DEFAULT_FEATURE_DIM

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS, SEED_INTENTS  # noqa: E402


# ==================================================================================
def _buildPolicy(device: str = "cpu") -> DCPolicy:
    options = buildOptions(
        embedDim=G_DEFAULT_EMBED_DIM,
        featureDim=G_DEFAULT_FEATURE_DIM,
        freezeBackbone=True,
        stackSize=4,
        durationSec=1.0,
    )
    return DCPolicy(options, device=device)


def test_carousel_initialized_to_stack_size() -> None:
    policy = _buildPolicy()
    assert len(policy._carousel) == 4
    for visual, actionEmb, param in policy._carousel:
        assert visual.shape == (3, 224, 224)
        assert actionEmb.ndim == 1
        assert param.shape == (8,)


def test_forward_shapes_full_context() -> None:
    policy = _buildPolicy()
    image = np.random.randint(0, 255, (480, 360, 3), dtype=np.uint8)

    out = policy.forward(
        image,
        intent="login",
        action="down",
        parameters={"kind": "coordinate", "x": 0.5, "y": 0.5},
    )

    assert set(out.keys()) == {"ACTIONS", "ARGKINDS", "SPATIAL"}
    assert out["ACTIONS"].shape[-1] == G_DEFAULT_EMBED_DIM
    assert out["ARGKINDS"].shape[-1] == G_DEFAULT_EMBED_DIM
    assert out["SPATIAL"].shape[-1] == 4


def test_predict_contract() -> None:
    policy = _buildPolicy()
    image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)

    actionKey, argument = policy.predict(
        image,
        intent="browse",
        action=C_NONE_ACTION,
        parameters=None,
    )

    assert actionKey in SEED_ACTIONS
    assert isinstance(argument, dict)
    assert argument["kind"] in SEED_ARGUMENT_KINDS


def test_stride_skips_push_when_too_soon() -> None:
    policy = _buildPolicy()
    image = np.zeros((32, 32, 3), dtype=np.uint8)

    policy.forward(image, intent="idle", action="move", timestamp=0.0)
    lastVisual = policy._carousel[-1][0].clone()

    policy.forward(image, intent="idle", action="up", timestamp=0.1)
    assert torch.equal(policy._carousel[-1][0], lastVisual)

    policy.forward(image, intent="idle", action="up", timestamp=0.25)
    assert len(policy._carousel) == 4


def test_missing_vocabularies_raise_via_options() -> None:
    options = PolicyOptions(actions=None, argumentKinds=None, intents=None)
    try:
        options.validate()
        raised = False
    except ValueError:
        raised = True
    assert raised
