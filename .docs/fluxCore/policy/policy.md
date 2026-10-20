## Overview & Design Context

Policy at `src/fluxCore/policy/__policy.py`.

One array of images → `(actionKey, argument)` where argument is a **variant** dict:

| kind | payload |
|------|---------|
| `coordinate` | `x`, `y` (normalized) |
| `box` | `left`, `top`, `width`, `height` |
| `key` | `code` (from key registry fixed at init) |
| `text` | `value` (from text registry fixed at init) |

Action / key / text vocabularies are **defined when the Policy is constructed** (or when a matching checkpoint is loaded). There is no runtime `setRegistry`.

---

## Classes

### `Policy`
- **Public:**
  - `forward(imageArray)` → dict of tensors for training
  - `predict(imageArray)` → `(actionKey, argumentDict)`
  - `actionKeys` → vocabulary fixed at init
- **Removed:** `setRegistry`, `reset`

## Constants

- `C_SEED_ACTION_KEYS` — optional seed labels
- `C_DEFAULT_FEATURE_DIM` — `512`
- `C_ARG_KINDS` — `("coordinate", "box", "key", "text")`

## Sample Usage

```python
policy = Policy(
    actRegEmbeddings=actionEmb,
    actKeys=["down", "up", "move", "inject"],
    keyRegEmbeddings=keyEmb,   # optional
    keyCodes=["A", "TAB", "ESCAPE"],
    textRegEmbeddings=textEmb, # optional
    textValues=["login", "submit"],
)

actionKey, argument = policy.predict(imageArray)
# e.g. ("move", {"kind": "coordinate", "x": 0.42, "y": 0.61})
# e.g. ("inject", {"kind": "key", "code": "TAB"})
# e.g. ("inject", {"kind": "text", "value": "login"})
```
