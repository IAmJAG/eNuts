# ==================================================================================
"""Smoke: StreamingPolicy carousel, time gate, dual frame types."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
import sys

# ==================================================================================
import numpy as np
import torch

# ==================================================================================
from fluxCore.policy import StreamingPolicy

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS  # noqa: E402


# ==================================================================================
def test_step_ndarray_predicts_with_padding() -> None:
    trace("test_step_ndarray_predicts_with_padding")
    options = buildOptions(stackSize=4, durationSec=1.0, embedDim=64, featureDim=256)
    policy = StreamingPolicy(options, device="cpu")

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result = policy.step(frame, timestamp=0.0)
    assert result is not None
    actionKey, argument = result
    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
    assert len(policy._carousel) == 1
    assert policy._carousel[0].device == policy._device
    trace("  PASS")


def test_time_gate_drops_too_soon() -> None:
    trace("test_time_gate_drops_too_soon")
    options = buildOptions(stackSize=4, durationSec=1.0, embedDim=64, featureDim=256)
    policy = StreamingPolicy(options, device="cpu")

    frame = torch.rand(3, 100, 100)
    assert policy.step(frame, 0.0) is not None
    assert policy.step(frame, 0.1) is None
    assert policy.step(frame, 0.25) is not None
    assert len(policy._carousel) == 2
    trace("  PASS")


def test_tensor_and_ndarray_both_accepted() -> None:
    trace("test_tensor_and_ndarray_both_accepted")
    options = buildOptions(stackSize=4, durationSec=10.0, embedDim=64, featureDim=256)
    policy = StreamingPolicy(options, device="cpu")

    assert policy.step(np.zeros((64, 64, 3), dtype=np.uint8), 0.0) is not None
    assert policy.step(torch.zeros(3, 64, 64), 3.0) is not None
    assert len(policy._carousel) == 2
    for frame in policy._carousel:
        assert frame.device == policy._device
    trace("  PASS")


def test_reset_clears_runtime_state() -> None:
    options = buildOptions(stackSize=4, durationSec=1.0, embedDim=64, featureDim=256)
    policy = StreamingPolicy(options, device="cpu")
    policy.step(torch.rand(3, 32, 32), 0.0)
    policy.reset()
    assert len(policy._carousel) == 0
    assert policy.step(torch.rand(3, 32, 32), 0.05) is not None
