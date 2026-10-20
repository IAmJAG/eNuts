# Implementation Details

## 1. Vocabulary layer

```text
VocabularyItem  → toEmbedding()     [embedDim]
Vocabulary      → toEmbeddings()    [N, embedDim]
PolicyOptions   → actions, argumentKinds (+ settings)
Policy          → scores against action / kind embedding tables
                → spatial head for continuous payload
```

## 2. Predict packing

| kind | argument dict |
|------|----------------|
| coordinate | `{kind, x, y}` |
| box | `{kind, left, top, width, height}` |
| key | `{kind, code}` — value open (empty until value path exists) |
| text | `{kind, value}` — value open (empty until value path exists) |
