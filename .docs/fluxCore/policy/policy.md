## Overview

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py` → **`DCPolicy`** (`CP_VERSION` **2.0**)

### Context model

```text
intent                          ← blanket over the whole stack
  carousel[t] = (visual_t, action_t, parameters_t)
```

Missing action/params use pads (`NONE` / empty), not omitted channels.

```text
src/fluxCore/policy/
  __dcPolicy.py          DCPolicy
  __policyOptions.py     PolicyOptions (+ pad constants)
  vocabulary/
    __vocabulary.py              Vocabulary[TLabel]
    __actionVocabulary.py        ActionVocabulary
    __argumentKindVocabulary.py  ArgumentKindVocabulary
    __intentVocabulary.py        IntentVocabulary
    labels/
      Label, ActionLabel, ArgumentKindLabel, IntentLabel
```

| Discrete (typed vocabulary) | Continuous / open |
|----------------------------|-------------------|
| `ActionVocabulary` / `ActionLabel` (incl. `NONE`) | spatial x,y / box |
| `ArgumentKindVocabulary` / `ArgumentKindLabel` (incl. `none`) | key code, text value |
| `IntentVocabulary` / `IntentLabel` | — |

---

## Pipeline

```text
image + action + parameters  → slot → carousel[T]
intent                       → embed
slot stack → backbone(visual) + actionEmb + paramVec
           → slotMerge → mean over T → contextMerge(intent) → h
h → action / arg-kind / spatial heads → cosine / pack
```

Accept interval: `durationSec / stackSize` (`PolicyOptions.acceptIntervalSec`).

---

## API

```python
from fluxCore.policy import (
    DCPolicy,
    PolicyOptions,
    ActionVocabulary,
    ArgumentKindVocabulary,
    IntentVocabulary,
    C_NONE_ACTION,
    C_NONE_ARGUMENT_KIND,
)

options = PolicyOptions(
    actions=ActionVocabulary({
        "NONE": "pad", "down": "down", "up": "up", "move": "move", "inject": "inject",
    }),
    argumentKinds=ArgumentKindVocabulary({
        "none": "pad", "coordinate": "pt", "box": "box", "key": "key", "text": "text",
    }),
    intents=IntentVocabulary({"idle": "idle", "login": "login"}),
    stackSize=16,
    durationSec=2.0,
)
options.validate()
policy = DCPolicy(options, device="cuda")

out = policy.forward(
    image,
    intent="login",
    action="down",
    parameters={"kind": "coordinate", "x": 0.5, "y": 0.4},
    timestamp=0.0,
)
action, argument = policy.predict(
    image, intent="login", action=C_NONE_ACTION, parameters=None, timestamp=0.25,
)

policy.save("policy.pt")
policy = DCPolicy.load("policy.pt", options=options, device="cuda")
```

### Persistence

| Artifact | Contents |
|----------|----------|
| Options JSON | typed vocabs (actions, argumentKinds, intents), stack, duration, … |
| Weight file | `{ VERSION: "2.0", MODELSTATE }` |

Carousel is runtime-only.

---

## PolicyOptions

| Field | Type |
|-------|------|
| `actions` | `ActionVocabulary` |
| `argumentKinds` | `ArgumentKindVocabulary` |
| `intents` | `IntentVocabulary` |
| `featureDimension` | int (default 576) |
| `freezeBackbone` | bool |
| `stackSize` | ∈ {4, 8, 16, 32, 64} |
| `durationSec` | float > 0 |
| `acceptIntervalSec` | read-only: `durationSec / stackSize` |

Pads: `C_NONE_ACTION` (`"NONE"`), `C_NONE_ARGUMENT_KIND` (`"none"`).

`validate()` requires all three vocabularies non-empty.

---

## Vocabulary layer

- Base: `Vocabulary[TLabel]` with `toTensor()` → `[N, dimension]`
- Typed subclasses: `ActionVocabulary`, `ArgumentKindVocabulary`, `IntentVocabulary`
- Labels: `Label`, `ActionLabel`, `ArgumentKindLabel`, `IntentLabel`
- Embeddings are **cached on `DCPolicy`** at construction
