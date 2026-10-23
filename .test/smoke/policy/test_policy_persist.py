# ==================================================================================
"""Smoke: options JSON separate from weights; DCPolicy v2 save/load."""
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
from fluxCore.policy import C_NONE_ACTION, DCPolicy, PolicyOptions

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.policy.builders import buildOptions  # noqa: E402
from fixtures.policy.seeds import SEED_ACTIONS, SEED_ARGUMENT_KINDS  # noqa: E402


# ==================================================================================
def test_save_load_weights_with_separate_options(tmp_path: Path) -> None:
    options = buildOptions(embedDim=64, featureDim=576, freezeBackbone=True, stackSize=4)
    policy = DCPolicy(options, device="cpu")

    optionsPath = tmp_path / "policy_options.json"
    weightsPath = tmp_path / "policy.pt"

    with optionsPath.open("w", encoding="utf-8") as handle:
        json.dump(options.encode(), handle, indent=2)
    policy.save(weightsPath)

    blob = torch.load(weightsPath, map_location="cpu", weights_only=False)
    assert set(blob.keys()) == {"VERSION", "MODELSTATE"}
    assert blob["VERSION"] == DCPolicy.CP_VERSION

    restoredOptions = PolicyOptions()
    with optionsPath.open(encoding="utf-8") as handle:
        restoredOptions.decode(json.load(handle))
    restoredOptions.validate()
    assert restoredOptions.intents is not None

    loaded = DCPolicy.load(weightsPath, options=restoredOptions, device="cpu")
    image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    actionKey, argument = loaded.predict(
        image, intent="login", action=C_NONE_ACTION, parameters=None
    )

    assert actionKey in SEED_ACTIONS
    assert argument["kind"] in SEED_ARGUMENT_KINDS


def test_load_rejects_bad_version(tmp_path: Path) -> None:
    options = buildOptions(embedDim=64, featureDim=576, stackSize=4)
    path = tmp_path / "bad.pt"
    torch.save({"VERSION": "0.0", "MODELSTATE": {}}, path)

    try:
        DCPolicy.load(path, options=options, device="cpu")
        raised = False
    except ValueError:
        raised = True
    assert raised
