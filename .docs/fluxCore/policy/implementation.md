# Implementation — DCPolicy v2

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py` (`CP_VERSION` **2.0**).

## 1. Data path

```text
forward(image, intent, action, parameters, timestamp?)
  → accept gate (optional timestamp)
  → _push: visual transform + action embed + _encodeParameters
  → carousel[T] slots
  → backbone(visuals) || actionEmbs || params
  → _slotMerge → mean_t → cat(intentEmb) → _contextMerge → h
  → actionHead / argumentKindHead / spatialHead
  → predict: cosine vs cached tables → (actionKey, argumentDict)
```

## 2. Modules

| Module | Role |
|--------|------|
| `_transform` | Resize 224, ToTensor, ImageNet normalize |
| `_backbone` | MobileNet V3 Small → 576-d |
| `_slotMerge` | Linear(576 + actionDim + 8 → featureDim) |
| `_contextMerge` | Linear(featureDim + intentDim → featureDim) |
| `_actionHead` / `_argumentKindHead` / `_spatialHead` | decision |
| `_actionEmbeddings` / `_argKindEmbeddings` / `_intentEmbeddings` | cached buffers |

## 3. Parameter encoding (`C_PARAM_DIM` = 8)

| Indices | Content |
|---------|---------|
| 0–3 | spatial (x,y or left,top,width,height) |
| 4–5 | key/text hash folds |
| 6–7 | argument-kind embed snippet |

Empty / missing parameters → zeros.

## 4. Pads

| Constant | Value |
|----------|--------|
| `C_NONE_ACTION` | `"NONE"` |
| `C_NONE_ARGUMENT_KIND` | `"none"` |

Include these labels in the action / argument-kind vocabularies.

## 5. Phases

| Phase | Status |
|-------|--------|
| 0 Baseline image-only | superseded by v2 |
| 1 Options + intents + pads | **Done** |
| 2 Slot carousel + API | **Done** |
| 3 Encode/fuse full context | **Done** |
| 4 Tests + docs + CP_VERSION 2.0 | **Done** |
| 5 Training / richer temporal / key-text values | Deferred |

## 6. Predict packing

| kind | argument dict |
|------|----------------|
| coordinate | `{kind, x, y}` |
| box | `{kind, left, top, width, height}` |
| key | `{kind, code}` |
| text | `{kind, value}` |
| none | `{kind: none}` |

## 7. Checkpoint

```text
{ "VERSION": "2.0", "MODELSTATE": state_dict() }
```

Options JSON: actions, argumentKinds, intents, stackSize, durationSec, featureDimension, freezeBackbone.
