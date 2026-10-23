## Overview

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py` → **`DCPolicy`** (`CP_VERSION` **2.0**)

### Context model

```text
intent                          ← blanket over the whole stack
  carousel[t] = (visual_t, action_t, parameters_t)
```

At each visual, the **action taken** and its **parameters** are aligned with that frame. Intent encloses the trajectory. Missing action/params use pads (`NONE` / empty), not omitted channels.

```text
src/fluxCore/policy/
  __dcPolicy.py          DCPolicy
  __policyOptions.py     PolicyOptions (+ pad constants)
  vocabulary/            Vocabulary, ActionVocabulary, ArgumentKindVocabulary
  vocabulary/labels/     Label, …
```

| Discrete (vocabulary) | Continuous / open |
|----------------------|-------------------|
| actions (incl. `NONE`) | spatial x,y / box |
| argument kinds (incl. `none`) | key code, text value |
| intents | — |

---

## Pipeline

```text
image + action + parameters  → slot → carousel[T]
intent                       → embed
slot stack → backbone(visual) + actionEmb + paramVec
           → slotMerge → mean over T → contextMerge(intent) → h
h → action / arg-kind / spatial heads → cosine / pack
```

Accept interval: `durationSec / stackSize` (`acceptIntervalSec`). Optional `timestamp` gates whether a new slot is pushed.

---

## API

```python
from fluxCore.policy import (
    DCPolicy, PolicyOptions, Vocabulary,
    C_NONE_ACTION, C_NONE_ARGUMENT_KIND,
)

options = PolicyOptions(
    actions=Vocabulary({
        "NONE": "pad", "down": "down", "up": "up", "move": "move", "inject": "inject",
    }),
    argumentKinds=Vocabulary({
        "none": "pad", "coordinate": "pt", "box": "box", "key": "key", "text": "text",
    }),
    intents=Vocabulary({"idle": "idle", "login": "login"}),
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
| Options JSON | vocabs (actions, argumentKinds, intents), stack, duration, … |
| Weight file | `{ VERSION: "2.0", MODELSTATE }` |

Carousel is runtime-only.

---

## PolicyOptions

- `actions`, `argumentKinds`, `intents` — required by `validate()`
- `featureDimension` (default 576), `freezeBackbone`
- `stackSize` ∈ {4, 8, 16, 32, 64}, `durationSec` > 0
- `acceptIntervalSec` = `durationSec / stackSize` (`frameRate` is a legacy alias for the same interval)
- Pads: `C_NONE_ACTION` (`"NONE"`), `C_NONE_ARGUMENT_KIND` (`"none"`)

---

## Vocabulary

- `toTensor()` → `[N, dimension]`; cached on `DCPolicy` at init
- Labels under `vocabulary/labels/`
