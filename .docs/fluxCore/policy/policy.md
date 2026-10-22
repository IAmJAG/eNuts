## Overview & Design Context

```text
Policy              — stack tensor → action + argument (weights)
StreamingPolicy     — inherits Policy; carousel + time gate → predict
PolicyOptions       — vocab + featureDim + freezeBackbone + stackSize + durationSec
```

| Discrete vocabulary | Open argument values |
|---------------------|----------------------|
| actions | coordinate / box fields |
| argument kinds | key codes, free text |

---

## PolicyOptions

- `actions`, `argumentKinds`, `featureDimension`, `freezeBackbone`
- `stackSize` ∈ {4, 8, 16, 32, 64} — carousel capacity for StreamingPolicy
- `durationSec` > 0 — real-time span the stack represents (accept rate ≈ stackSize / durationSec)
- Frame type is **not** an option; push accepts `ndarray` or `Tensor`

## Policy

- `Policy(options, device="cpu")`
- `forward` / `predict(imageArray)` — `imageArray` is `[T,3,H,W]`
- Weights: `save(path)` / `load(path, options, device="cpu")` — no options inside `.pt`

## StreamingPolicy(Policy)

- Owns carousel, blank padding, time gate; decision via inherited `predict`
- `push(frame, timestamp) → (action, argument) | None` — None if frame not accepted
- Tick = every accepted frame written into the stack
- Pads leading blanks until `stackSize` real frames collected
- Runtime buffers are not persisted

```python
from fluxCore.policy import StreamingPolicy, PolicyOptions, Vocabulary

options = PolicyOptions(
    actions=Vocabulary({"down": "finger down", "up": "finger up"}),
    argumentKinds=Vocabulary({
        "coordinate": "point", "box": "rect", "key": "key", "text": "text",
    }),
    stackSize=16,
    durationSec=2.0,
)
policy = StreamingPolicy(options, device="cpu")
result = policy.push(frame, timestamp=0.0)  # ndarray or Tensor
```

## Persistence

| Artifact | Contents |
|----------|----------|
| Options JSON | full PolicyOptions including stackSize / durationSec |
| Weight file `.pt` | `{ version, model_state }` only |
