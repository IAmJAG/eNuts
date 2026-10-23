# Implementation — DCPolicy

**Source of truth:** `src/fluxCore/policy/__dcPolicy.py`.

## 1. Data path

```text
raw image (ndarray | Tensor)
  → _push: transform (Resize 224, ToTensor, Normalize)
  → _imageCarousel (deque, maxlen=stackSize)
  → _fuse(carousel) → features
  → actionHead / argumentKindHead / spatialHead
  → predict: cosine vs cached embedding buffers → (actionKey, argument)
```

## 2. Modules

| Module | Role |
|--------|------|
| `_transform` | torchvision Compose — classifier-style prep |
| `_backbone` | MobileNet V3 Small features + AdaptiveAvgPool2d + Flatten |
| `_actionHead` | feature → action embedding dim |
| `_argumentKindHead` | feature → argument-kind embedding dim |
| `_spatialHead` | feature → 4 × sigmoid |
| `_actionEmbeddings` / `_argKindEmbeddings` | registered buffers, device-locked |

## 3. Predict packing

| kind | argument dict |
|------|----------------|
| coordinate | `{kind, x, y}` |
| box | `{kind, left, top, width, height}` |
| key | `{kind, code}` — open (empty until value path exists) |
| text | `{kind, value}` — open (empty until value path exists) |

## 4. Checkpoint

```text
{
  "VERSION": DCPolicy.CP_VERSION,   # e.g. "1.0"
  "MODELSTATE": state_dict()
}
```

Load requires the matching `PolicyOptions` (separate JSON). Device is chosen at load time.

## 5. Related types

- `PolicyOptions` — serializable config
- `Vocabulary` / `ActionVocabulary` / `ArgumentKindVocabulary`
- `iPolicy` — `forward`, `predict`, `save`, `load`
