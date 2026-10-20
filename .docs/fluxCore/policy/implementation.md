# Implementation Details

## 1. Flow

```text
fused features
  ├─ actionHead  → score vs action registry → action key
  ├─ argKindHead → coordinate | box | key | text
  ├─ spatialHead → [x/left, y/top, w, h] in [0,1]
  ├─ keyHead     → score vs key registry → code
  └─ textHead    → score vs text registry → value
```

## 2. Public API

`forward`, `predict`, `actionKeys` only.

## 3. Argument packing (`predict`)

| kind | dict |
|------|------|
| coordinate | `{kind, x, y}` |
| box | `{kind, left, top, width, height}` |
| key | `{kind, code}` |
| text | `{kind, value}` |

Empty key/text registries yield empty `code` / `value` if that kind is still selected.
