## Overview & Design Context

`Vocabulary` holds a list of `VocabularyItem`s and a stacked embedding tensor. It is not called from `DCPolicy` or `DCPolicyCore`.

* **Design Decision / Deviation Notes:** Embeddings are rebuilt on add, remove, and fuse changes. Empty vocab leaves embeddings as `None`.

---

## Classes

### `Vocabulary`
- **Purpose:** Ordered discrete vocabulary with deterministic embeddings.
- **Methods:**
  - `__init__(vocabulary=None, dimension=128, fuse=False, device=None)` → stores items and builds embeddings.
  - `add(idItem, description=None, options=None)` → appends a string id or an item, then rebuilds.
  - `remove(idItem)` → drops by id (string or `iVocabularyItem`), then rebuilds.
  - `embeddings` / `ids` / `vocabulary` / `dimension` / `fuse` / `size` / `device` → properties. Setting `fuse` rebuilds.

---

## Functions

None.

---

## Constants & Globals

None. Default width is `G_DEFAULT_EMBED_DIM` (128) from utilities.

## Sample Usage

```python
from fluxCore.policy.vocabulary import Vocabulary

vocab = Vocabulary(dimension=128, fuse=True)
vocab.add("tap", description="screen tap", options={"kind": "point"})
print(vocab.embeddings.shape, vocab.ids)
```
