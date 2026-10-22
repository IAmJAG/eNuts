# ==================================================================================
"""Smoke: options JSON separate from weight file; Policy.save/load rebuild."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import json
from pathlib import Path
import sys

# ==================================================================================
import torch

# ==================================================================================
from fluxCore.policy import Policy, PolicyOptions

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS  # noqa: E402


# ==================================================================================
def test_save_load_weights_with_separate_options(tmp_path: Path) -> None:
    trace("test_save_load_weights_with_separate_options: build")
    options = buildOptions(embedDim=64, featureDim=256, freezeBackbone=True)
    policy = Policy(options, device="cpu")

    optionsPath = tmp_path / "policy_options.json"
    weightsPath = tmp_path / "policy.pt"

    with optionsPath.open("w", encoding="utf-8") as handle:
        json.dump(options.encode(), handle, indent=2)
    trace(f"  options written → {optionsPath}")

    policy.save(weightsPath)
    trace(f"  weights written → {weightsPath}")

    blob = torch.load(weightsPath, map_location="cpu", weights_only=False)
    assert set(blob.keys()) == {"version", "modelState"}
    assert "options" not in blob
    assert blob["version"] == Policy.CHECKPOINT_VERSION

    restoredOptions = PolicyOptions()
    with optionsPath.open(encoding="utf-8") as handle:
        restoredOptions.decode(json.load(handle))

    assert restoredOptions.actions is not None
    assert restoredOptions.argumentKinds is not None
    assert restoredOptions.actions.labels == options.actions.labels
    assert restoredOptions.argumentKinds.labels == options.argumentKinds.labels

    loaded = Policy.load(weightsPath, options=restoredOptions, device="cpu")
    imageArray = torch.rand(4, 3, 224, 224)
    actionKey, argument = loaded.predict(imageArray)
    trace(f"  predict actionKey={actionKey!r} argument={argument!r}")

    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS
    trace("test_save_load_weights_with_separate_options: PASS")


def test_load_rejects_bad_version(tmp_path: Path) -> None:
    options = buildOptions(embedDim=64, featureDim=256)
    path = tmp_path / "bad.pt"
    torch.save({"version": -1, "modelState": {}}, path)

    try:
        Policy.load(path, options=options, device="cpu")
        raised = False
    except ValueError:
        raised = True
    assert raised
