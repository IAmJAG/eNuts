# Implementation — DCPolicy

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py`.

## 1. Current data path (shipped)

```text
raw image
  → _toPil / _transform
  → _imageCarousel (zeros init, maxlen=stackSize)
  → accept gate (timestamp vs durationSec/stackSize)
  → _fuse → mean over T → [B, 576]
  → actionHead / argumentKindHead / spatialHead
  → predict: cosine vs cached buffers → (actionKey, argument)
```

## 2. Target data path

```text
intent (blanket)
image + action + parameters
  → slot (visual_t, action_t, params_t)
  → carousel[T]
  → encode each slot → temporal pool → merge intent → h
  → heads → next action + argument
```

## 3. Phased implementation plan

### Phase 0 — Baseline (done)

- `DCPolicy` image-only path, transform, zero carousel, stride, cached action/kind embeds
- `PolicyOptions.validate()`, persist `VERSION` / `MODELSTATE`
- Smoke tests on raw image

### Phase 1 — Options & vocab surface

**Files:** `__policyOptions.py`, `vocabulary/`, `__init__.py`, docs

- Add `intents: Vocabulary` (or `IntentVocabulary`)
- Extend `validate()` for non-empty intents
- Serialize intents in options JSON
- Pad tokens: document `NONE` action id + empty parameter encoding contract
- Rename clarity (optional): accept interval property name vs `frameRate`

**Exit:** options round-trip includes intents; `validate()` fails without them.

### Phase 2 — Slot carousel (structure)

**Files:** `__dcPolicy.py`

- Replace pure-image deque with slot structure: visual tensor + action id/emb + param vector
- Init `stackSize` slots with zero visual + NONE action + EMPTY params
- Extend `_push` / `forward` signature: `image, intent, action, parameters, timestamp=`
- Stride still gates whether a **new slot** is appended

**Exit:** carousel always length `stackSize`; API accepts full context; behavior can still ignore intent/action in fuse (wire only).

### Phase 3 — Encode & fuse full context

**Files:** `__dcPolicy.py`

- `_encodeParams(argument) →` fixed vector
- `_encodeSlot(visual, action, params)` after backbone on visual
- Temporal pool over slot vectors
- Intent embedding (cached buffer) merged into `h`
- Heads consume `h` (match `featureDimension`)

**Exit:** forward/predict use vision + action + params + intent; smoke tests pass with full args.

### Phase 4 — Hardening

**Files:** tests, docs, minor API

- Smoke: stride + full context; persist with intents in options
- `iPolicy` signature notes
- Checkpoint version bump if state_dict layout breaks (`CP_VERSION`)

**Exit:** tests green; docs match code.

### Phase 5 — Deferred product

- Training data format for (visual, action, params, intent) sequences
- Key/text value heads
- Stronger temporal model if mean pool is insufficient

---

## 4. Code hit list (target)

| Location | Change |
|----------|--------|
| `PolicyOptions` | `intents`, `validate()` |
| `DCPolicy.__init__` | intent buffers, slot pads, merge layers |
| `DCPolicy._push` | build slot |
| `DCPolicy._fuse` | slot encode + intent |
| `DCPolicy.forward` / `predict` | full context args |
| `vocabulary/` | intent type optional |
| `.test/smoke/policy/` | full context calls |

## 5. Modules (current)

| Module | Role |
|--------|------|
| `_transform` | classifier-style image prep |
| `_backbone` | MobileNet V3 Small → 576-d |
| `_actionHead` / `_argumentKindHead` / `_spatialHead` | decision heads |
| `_actionEmbeddings` / `_argKindEmbeddings` | cached tables |

## 6. Predict packing

| kind | argument dict |
|------|----------------|
| coordinate | `{kind, x, y}` |
| box | `{kind, left, top, width, height}` |
| key | `{kind, code}` |
| text | `{kind, value}` |

## 7. Checkpoint

```text
{ "VERSION": DCPolicy.CP_VERSION, "MODELSTATE": state_dict() }
```

Options (including future intents) stay in a separate JSON file.
