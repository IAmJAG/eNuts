## Overview & Design Context

Policy at `src/fluxCore/policy/__policy.py`, options at `__policyOptions.py`.

`PolicyOptions` and `RegistryOptions` extend `jAGFx.serializer.Serializable` so they can be persisted to JSON. **Labels** are stored in the file; **embeddings** are produced by the options layer (`RegistryOptions.embeddings()` / `PolicyOptions.actionEmbeddings()`), not written to disk.

---

## Classes

### `RegistryOptions` (Serializable)
- **Persisted:** `labels`, `descriptions` (optional), `embedDim`
- **Computed:** `embeddings()` → `[N, embedDim]` deterministic unit vectors from label strings

### `PolicyOptions` (Serializable)
- **Persisted:** `action`, `key`, `text`, `argKinds`, `featureDim`, `freezeBackbone`, `device`, `embedDim`
- **Helpers:** `actionEmbeddings()`, `keyEmbeddings()`, `textEmbeddings()`, `requireAction()`

### `Policy`
- **Init:** `Policy(options: PolicyOptions)` only
- **Public:** `forward`, `predict`, `actionKeys`

## Sample Usage

```python
from fluxCore.policy import Policy, PolicyOptions, RegistryOptions, C_SEED_ACTION_KEYS
import json

options = PolicyOptions(
    action=RegistryOptions(labels=list(C_SEED_ACTION_KEYS)),
    key=RegistryOptions(labels=["A", "TAB", "ESCAPE"]),
    text=RegistryOptions(labels=["login", "submit"]),
    device="cpu",
)

# Persist
blob = options.encode()
with open("policyOptions.json", "w", encoding="utf-8") as f:
    json.dump(blob, f, indent=2)

# Reload
loaded = PolicyOptions()
with open("policyOptions.json", encoding="utf-8") as f:
    loaded.decode(json.load(f))

policy = Policy(loaded)
actionKey, argument = policy.predict(imageArray)
```
