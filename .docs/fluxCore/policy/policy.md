## Overview

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py` → **`DCPolicy`**

Discrete–Continuous Policy: one raw frame in → transform + image carousel → fused features → discrete action / argument kind (embedding cosine) + continuous spatial payload.

```text
src/fluxCore/policy/
  __dcPolicy.py          DCPolicy (base model)
  __policyOptions.py     PolicyOptions
  vocabulary/            Vocabulary, ActionVocabulary, ArgumentKindVocabulary
  vocabulary/labels/     Label, ActionLabel, ArgumentKindLabel
```

| Discrete (vocabulary) | Continuous / open |
|----------------------|-------------------|
| actions | spatial x,y / box |
| argument kinds | key code, text value |

---

## DCPolicy

| Concern | Behavior |
|---------|----------|
| Input | **Raw** image (`Tensor` or `ndarray`) — not a pre-stacked batch |
| Transform | `Resize(224)`, `ToTensor`, ImageNet `Normalize` (owned by the policy) |
| Carousel | `deque` capacity = `PolicyOptions.stackSize` |
| Backbone | MobileNet V3 Small features + pool + flatten |
| Heads | action embed, argument-kind embed, spatial `[4]` + sigmoid |
| Scoring | cosine vs **cached** embedding buffers (fixed for instance lifetime) |
| Device | argument, default `"cuda"` (falls back via `getTorchDevice`) |

### API

```python
from fluxCore.policy import DCPolicy, PolicyOptions, Vocabulary

options = PolicyOptions(
    actions=Vocabulary({"down": "finger down", "up": "finger up"}),
    argumentKinds=Vocabulary({
        "coordinate": "point",
        "box": "rect",
        "key": "key",
        "text": "text",
    }),
    stackSize=16,
    durationSec=2.0,
    freezeBackbone=True,
)

policy = DCPolicy(options, device="cuda")

# raw frame each step — policy transforms and updates carousel
logits = policy.forward(image)           # dict: ACTIONS, ARGKINDS, SPATIAL
action, argument = policy.predict(image) # (str, dict)

policy.save("policy.pt")                 # VERSION + MODELSTATE only
policy = DCPolicy.load("policy.pt", options=options, device="cuda")
```

### Persistence

| Artifact | Contents |
|----------|----------|
| Options JSON | `PolicyOptions.encode()` (vocab, stackSize, durationSec, …) |
| Weight file | `{ VERSION, MODELSTATE }` — no options inside |

Carousel / runtime stream state is **not** saved.

---

## PolicyOptions

- `actions`, `argumentKinds` — vocabularies
- `featureDimension`, `freezeBackbone`
- `stackSize` ∈ {4, 8, 16, 32, 64}
- `durationSec` > 0 (time narrative for streaming accept rate when used)
- Device is **not** an option; pass at construct / load

---

## Vocabulary

- `Vocabulary` / `ActionVocabulary` / `ArgumentKindVocabulary`
- Labels under `vocabulary/labels/`
- `toTensor()` → `[N, dimension]` deterministic embeddings; **cached on DCPolicy** at init
