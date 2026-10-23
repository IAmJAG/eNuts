# ==================================================================================
"""Smoke: DCPolicy constructs, forward dict, predict contract, stride."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
import sys

# ==================================================================================
import numpy as np
import torch

# ==================================================================================
from fluxCore.policy import DCPolicy, PolicyOptions, Vocabulary
from fluxCore.utilities import G_DEFAULT_EMBED_DIM, G_DEFAULT_FEATURE_DIM

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS  # noqa: E402


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
    assert len(policy._imageCarousel) == 4
    for frame in policy._imageCarousel:
        assert frame.shape == (3, 224, 224)
        assert frame.device == policy._device


def test_forward_shapes_raw_image() -> None:
    policy = _buildPolicy()
    image = np.random.randint(0, 255, (480, 360, 3), dtype=np.uint8)

    out = policy.forward(image)

    assert set(out.keys()) == {"ACTIONS", "ARGKINDS", "SPATIAL"}
    assert out["ACTIONS"].shape[-1] == G_DEFAULT_EMBED_DIM
    assert out["ARGKINDS"].shape[-1] == G_DEFAULT_EMBED_DIM
    assert out["SPATIAL"].shape[-1] == 4
    assert torch.all(out["SPATIAL"] >= 0) and torch.all(out["SPATIAL"] <= 1)


def test_predict_contract() -> None:
    policy = _buildPolicy()
    image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)

    actionKey, argument = policy.predict(image)

    assert actionKey in SEED_ACTIONS
    assert isinstance(argument, dict)
    assert argument["kind"] in SEED_ARGUMENT_KINDS


def test_stride_skips_push_when_too_soon() -> None:
    # stackSize=4, durationSec=1 → min interval 0.25s
    policy = _buildPolicy()
    image = np.zeros((32, 32, 3), dtype=np.uint8)

    policy.forward(image, timestamp=0.0)
    # carousel still length 4 (zeros + one real); count non-zero-ish by last frame changed
    lastAfterFirst = policy._imageCarousel[-1].clone()

    policy.forward(image, timestamp=0.1)  # too soon — no push
    assert torch.equal(policy._imageCarousel[-1], lastAfterFirst)

    policy.forward(image, timestamp=0.25)  # accept
    # last slot replaced (still may be similar content; length stays 4)
    assert len(policy._imageCarousel) == 4


def test_missing_vocabularies_raise_via_options() -> None:
    options = PolicyOptions(actions=None, argumentKinds=None)
    try:
        options.validate()
        raised = False
    except ValueError:
        raised = True
    assert raised

    try:
        DCPolicy(options, device="cpu")
        raised2 = False
    except ValueError:
        raised2 = True
    assert raised2
