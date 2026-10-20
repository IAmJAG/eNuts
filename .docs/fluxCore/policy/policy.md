## Overview & Design Context

Policy starts from **vocabularies** — finite discrete sets.

| Discrete (vocabulary) | Open / continuous (not vocabulary) |
|------------------------|-------------------------------------|
| **actions** | coordinate / box spatial values |
| **argumentKinds** | key codes, free text values |

Key and text are argument *kinds*. Their *values* are not closed lists.

---

## Classes

### `VocabularyItem` (Serializable)
- `label`, `description`, `embedDim`
- `toEmbedding()` → `[embedDim]`

### `Vocabulary` (Serializable)
- ordered list of `VocabularyItem`
- `toEmbeddings()` → `[N, embedDim]`
- `fromLabels(...)` helper

### `PolicyOptions` (Serializable)
- `actions: Vocabulary`
- `argumentKinds: Vocabulary`
- model settings (`featureDim`, `freezeBackbone`, `device`, `embedDim`)
- `withDefaults()` seed builder

### `Policy`
- `Policy(options)`
- `predict` → `(actionKey, argumentDict)`

## Sample Usage

```python
from fluxCore.policy import Policy, PolicyOptions, Vocabulary
import json

options = PolicyOptions.withDefaults(device="cpu")
# or:
# options = PolicyOptions(
#     actions=Vocabulary.fromLabels(["down", "up", "move", "inject"]),
#     argumentKinds=Vocabulary.fromLabels(["coordinate", "box", "key", "text"]),
#     device="cpu",
# )

json.dump(options.encode(), open("policyOptions.json", "w"), indent=2)

loaded = PolicyOptions()
loaded.decode(json.load(open("policyOptions.json")))

policy = Policy(loaded)
actionKey, argument = policy.predict(imageArray)
```
