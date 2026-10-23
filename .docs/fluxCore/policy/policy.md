## Overview

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py` → **`DCPolicy`**

Discrete–continuous policy for UI/device automation.

### Context model (target)

```text
intent                          ← blanket over the whole stack
  carousel[t] = (visual_t, action_t, parameters_t)
```

At each visual, the **action taken** and its **parameters** are aligned with that frame. Intent encloses the trajectory. The model always sees the full joint context (pads for missing action/params, not omitted channels).

```text
src/fluxCore/policy/
  __dcPolicy.py          DCPolicy
  __policyOptions.py     PolicyOptions
  vocabulary/            Vocabulary, ActionVocabulary, ArgumentKindVocabulary, …
  vocabulary/labels/     Label, ActionLabel, ArgumentKindLabel, …
```

| Discrete (vocabulary) | Continuous / open |
|----------------------|-------------------|
| actions | spatial x,y / box |
| argument kinds | key code, text value |
| intents (planned) | — |

---

## Current vs target

| | **Current (shipped)** | **Target (phased)** |
|--|----------------------|---------------------|
| Input | raw image (+ optional timestamp) | image + intent + action + parameters (+ timestamp) |
| Carousel | visuals only (zero-filled) | slots `(visual, action, params)` |
| Fusion | backbone mean over frames | per-slot merge → temporal pool → intent merge |
| Output | action + argument dict | same |

See `requirement.md` and `implementation.md` for phases and code hit list.

---

## DCPolicy (current behavior)

| Concern | Behavior |
|---------|----------|
| Input | Raw image (`PIL` / `ndarray` / `Tensor`) |
| Transform | Resize 224, ToTensor, ImageNet Normalize |
| Carousel | `stackSize` slots, init zeros; accept interval = `durationSec / stackSize` |
| Backbone | MobileNet V3 Small → 576-d features |
| Heads | action embed, argument-kind embed, spatial `[4]` |
| Scoring | cosine vs **cached** embedding buffers |
| Device | argument, default cuda (fallback cpu) |

```python
from fluxCore.policy import DCPolicy, PolicyOptions, Vocabulary

options = PolicyOptions(
    actions=Vocabulary({"down": "finger down", "up": "finger up"}),
    argumentKinds=Vocabulary({
        "coordinate": "point", "box": "rect", "key": "key", "text": "text",
    }),
    stackSize=16,
    durationSec=2.0,
)
policy = DCPolicy(options, device="cuda")
out = policy.forward(image, timestamp=0.0)
action, argument = policy.predict(image, timestamp=0.0)
```

### Persistence

| Artifact | Contents |
|----------|----------|
| Options JSON | `PolicyOptions.encode()` |
| Weight file | `{ VERSION, MODELSTATE }` only |

Carousel is runtime-only.

---

## PolicyOptions

- `actions`, `argumentKinds` — required via `validate()`
- `featureDimension` (default 576), `freezeBackbone`
- `stackSize` ∈ {4, 8, 16, 32, 64}, `durationSec` > 0
- `frameRate` property = `durationSec / stackSize` (accept **interval** in seconds)
- Planned: `intents` vocabulary

---

## Vocabulary

- `toTensor()` → `[N, dimension]`; cached on `DCPolicy` at init
- Labels under `vocabulary/labels/`
