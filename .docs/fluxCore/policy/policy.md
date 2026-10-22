## Overview & Design Context

Vocabulary is the foundation of the discrete side of the policy.

```text
src/fluxCore/policy/vocabulary/
  Label       — id + description (Serializable)
  Vocabulary  — dict of labels, toTensor() → embedding table

src/fluxCore/types/interface/policy/vocabulary/
  iLabel, iVocabulary
```

| Discrete vocabulary | Open argument values |
|---------------------|----------------------|
| actions | coordinate / box fields |
| argument kinds | key codes, free text |

---

## Classes

### `Label`
- `id`, `description`
- Serializable

### `Vocabulary`
- `Vocabulary({"down": "finger down", ...})`
- `dimension` (embed width), `size` / `labels`, `toTensor()` → `[N, dimension]`
- encode/decode: plain entry maps

### `PolicyOptions`
- `actions`, `argumentKinds`, `featureDimension`, `freezeBackbone`
- Serializable (`encode` / `decode`) — **persisted as its own JSON file**
- Does not own device or seed data

### `Policy`
- `Policy(options, device="cpu")`
- `forward` / `predict`
- **Weights only:** `save(path)` / `load(path, options, device="cpu")`

## Persistence

| Artifact | Contents |
|----------|----------|
| Options JSON | `PolicyOptions.encode()` |
| Weight file `.pt` | `{ version, model_state }` only |

Device is never stored; it is an argument (default `cpu`) at construct/load.

```python
import json
from fluxCore.policy import Policy, PolicyOptions, Vocabulary

options = PolicyOptions(
    actions=Vocabulary({"down": "finger down", "up": "finger up"}),
    argumentKinds=Vocabulary({
        "coordinate": "point",
        "box": "rect",
        "key": "keycode",
        "text": "string",
    }),
)
policy = Policy(options, device="cpu")

with open("policy_options.json", "w", encoding="utf-8") as f:
    json.dump(options.encode(), f, indent=2)
policy.save("policy.pt")

restoredOptions = PolicyOptions()
with open("policy_options.json", encoding="utf-8") as f:
    restoredOptions.decode(json.load(f))

policy = Policy.load("policy.pt", options=restoredOptions, device="cpu")
actionKey, argument = policy.predict(imageArray)
```
