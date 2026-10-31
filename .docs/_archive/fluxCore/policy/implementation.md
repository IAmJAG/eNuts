> **ARCHIVED 2026-10-31 — REFERENCE ONLY**  
> This file is no longer the source of truth. Active documentation will be rewritten under `.docs/fluxCore/policy/`. See `.docs/_archive/fluxCore/policy/README.md`.

---

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

## 2. Typed options & vocabulary

| Options field | Type | Labels |
|---------------|------|--------|
| `actions` | `ActionVocabulary` | `ActionLabel` |
| `argumentKinds` | `ArgumentKindVocabulary` | `ArgumentKindLabel` |
| `intents` | `IntentVocabulary` | `IntentLabel` |

Base class: `Vocabulary[TLabel]`. Subclasses live under `src/fluxCore/policy/vocabulary/`.

`PolicyOptions.validate()` requires all three non-empty.

## 3. Modules

| Module | Role |
|--------|------|
| `_transform` | Resize 224, ToTensor, ImageNet normalize |
| `_backbone` | MobileNet V3 Small → 576-d |
| `_slotMerge` | Linear(576 + actionDim + 8 → featureDim) |
| `_contextMerge` | Linear(featureDim + intentDim → featureDim) |
| `_actionHead` / `_argumentKindHead` / `_spatialHead` | decision |
| `_actionEmbeddings` / `_argKindEmbeddings` / `_intentEmbeddings` | cached buffers from typed vocabs |

## 4. Parameter encoding (`C_PARAM_DIM` = 8)

| Indices | Content |
|---------|---------|
| 0–3 | spatial |
| 4–5 | key/text hash folds |
| 6–7 | argument-kind embed snippet |

## 5. Pads

| Constant | Value |
|----------|--------|
| `C_NONE_ACTION` | `"NONE"` |
| `C_NONE_ARGUMENT_KIND` | `"none"` |

## 6. Phases

| Phase | Status |
|-------|--------|
| 1–4 Full context + tests | **Done** |
| Typed intent/action/arg vocab | **Done** (user) |
| 5 Training / richer temporal / key-text values | Deferred |

## 7. Checkpoint

```text
{ "VERSION": "2.0", "MODELSTATE": state_dict() }
```

Options JSON serializes the three typed vocabularies plus stack/duration/feature settings.
