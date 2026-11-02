## Overview & Design Context

`VocabularyItem` is one discrete entry: id, description, options. Description is stored and is not used in `toTensor`.

* **Design Decision / Deviation Notes:** Id and options are separate deterministic embeddings. `fuse=True` concatenates them.

---

## Classes

### `VocabularyItem`
- **Purpose:** One vocabulary row.
- **Methods:**
  - `__init__(id, description="", options=None)` → stores the three fields.
  - `copy()` / `__copy__()` → new item with the same fields.
  - `toTensor(dimension, fuse=False, device="cuda")` → id embedding, or `cat(id, options)` when `fuse` is true.
  - `id` / `description` / `options` → properties.

---

## Functions

None. Embedding is `deterministicEmbedding` from `fluxCore.utilities`.

---

## Constants & Globals

None.

## Sample Usage

```python
from fluxCore.policy.vocabulary import VocabularyItem

item = VocabularyItem("tap", description="screen tap", options={"kind": "point"})
vec = item.toTensor(128, fuse=True)
```
