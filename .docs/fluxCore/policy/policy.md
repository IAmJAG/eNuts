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
- `dimension`, `labels`, `toTensor()` → `[N, embedDim]`
- Serializable (`entries` + `embedDim`)

### `PolicyOptions`
- `actions: Vocabulary`, `argumentKinds: Vocabulary`
- `withDefaults()`

### `Policy`
- `Policy(options)` → `predict` → `(actionKey, argumentDict)`

## Sample

```python
from fluxCore.policy import Policy, PolicyOptions, Vocabulary

options = PolicyOptions.withDefaults(device="cpu")
# or:
options = PolicyOptions(
    actions=Vocabulary({"down": "finger down", "up": "finger up"}),
    argumentKinds=Vocabulary({
        "coordinate": "point",
        "box": "rect",
        "key": "keycode",
        "text": "string",
    }),
    device="cpu",
)

policy = Policy(options)
actionKey, argument = policy.predict(imageArray)
```
