# Requirements & Design Specifications

## 1. Project Overview

This document captures the redesigned requirements for the policy (model) component of the eNuts automation system.

The policy is responsible for deciding the next discrete action and its continuous arguments given the current high-level intent, a temporal stack of sequential streaming images, and the history of previously executed actions together with their arguments.

This is a redesign relative to the earlier architecture note in `.docs/hybrid_discrete_continuous_policy.md`. The earlier document remains for historical reference; all new design and implementation work must follow the requirements stated here.

## 2. Functional Requirements

- **FR-1 (Policy Inputs):** The policy must accept exactly three inputs at inference time:
  1. Current intent (key only).
  2. Image input (single image or pre-stacked tensor/ndarray). The policy (or its immediate pre-processing path) is responsible for stabilizing the visual input.
  3. Stack of previously taken actions together with their corresponding action arguments (action history).

- **FR-2 (Policy Outputs):** Given the inputs above, the policy must produce:
  1. The next discrete action key.
  2. The argument payload for that action (variant type).

- **FR-3 (Stateless Inference Contract):** The policy itself is a pure function of the three supplied inputs. History buffering (image carousel + action history), intent management, and final denormalization/execution are the responsibility of the surrounding Policy Wrapper, not of the model weights.

## 3. Non-Functional Requirements

- **NFR-1:** The input and output interfaces must be stable and explicitly typed so that the policy can be trained offline and later loaded into the live eNuts process without interface drift.
- **NFR-2:** Documentation for every source file that implements or consumes the policy must follow the path-mirroring and triad rules defined in `.kilocode/rules/Documentation.md`.
- **NFR-3:** Spatial arguments are expressed in normalized [0, 1] space. The Policy Wrapper denormalizes them using the current device resolution at execution time so the model remains resolution-agnostic.

## 4. Locked Design Decisions

### 4.1 Intent Schema

```text
Intent = {
  key: string,          // hex code or short text token, e.g. "ABCDEF1234567890" or "LOGIN"
  description: string   // human-readable meaning (lives only in the registry)
}
```

- The policy receives only the `key` (or an embedding derived from it).
- The intent registry is immutable and holds the full `{key, description}` pairs.
- First version uses a single current intent key. An array of keys can be added later if multi-intent is required.

### 4.2 Image Stack & Pre-processing

| Aspect | Decision |
|--------|----------|
| Accepted input | `ndarray` or `torch.Tensor` (single image or already-stacked) |
| Source | Out of scope for the policy design. Upstream will supply H.264-decoded frames converted to ndarray/tensor. |
| Pre-processing | Mandatory: resize, normalize, colour conversion, etc. so the model always sees a stable internal representation. |
| Temporal storage | Carousel (ring buffer) of the last *N* pre-processed frames. Owned by the Policy Wrapper (see FR-3). |
| Stack size *N* | **Default 16** (hyper-parameter, previously considered range 16–64). |
| Stride | Hyper-parameter. Guidance by source FPS so that the 16-frame window covers a comparable real-time duration:<br>• 30 fps → stride 1 (every frame)<br>• 60 fps → stride 3–4 |
| Internal tensor shape after pre-processing | **24 × 24 × 3** (H×W×C). Dtype and value range still open. |
| Preferred flow | Accept single image → pre-process → push into carousel → produce stacked tensor for the decision head. |

Purpose of the stack: give the model a sense of direction / temporal context.

**Note on 24×24×3:** This is a deliberate low-resolution choice. It reduces compute and memory but discards most fine spatial detail. Compatibility with a MobileNetV3-Small backbone (normally trained at 224×224) must be validated; a lighter custom CNN or a heavily adapted backbone may be required.

### 4.3 Discrete Action Registry (first version)

```text
[
  { key: "down",   description: "finger/right mouse button down" },
  { key: "up",     description: "finger/right mouse button up" },
  { key: "move",   description: "finger/mouse move" },
  { key: "inject", description: "send key" }
]
```

- Registry is immutable.
- Maps cleanly onto existing `fluxCore` gesture and key-injection primitives (`Touch`, `Tap`, key injection).

### 4.4 Argument Schema (variant)

Arguments are a discriminated variant:

| Kind | Shape | Notes |
|------|-------|-------|
| `box` | `{ top, left, width, height }` | Normalized [0, 1] relative to current screen |
| `coordinate` | `{ x, y }` | Normalized [0, 1] |
| `key` | single key token (`"A"`, `"<TAB>"`, `"<ESCAPE>"`, …) | |
| `text` | string | |

The policy outputs an action key plus an argument object that carries a type tag and the corresponding payload.

**Resolution change implication:** Because spatial values are normalized, a change of device resolution or orientation only affects the final denormalization step performed by the Policy Wrapper. Model weights remain valid.

### 4.5 Action + Argument History Stack

Fixed-length (or padded) history of the last *M* executed steps. Each step:

```text
{
  action_key: string,     // "down" | "up" | "move" | "inject" | …
  arguments: variant      // one of the shapes defined in 4.4
}
```

(or the equivalent tensor form: action IDs + padded argument tensor + mask).

### 4.6 Training Data

Primary scenario for the first implementation:

- **Recorded data** — video (H.264 or already-decoded frames) coupled with a timestamped log of gestures/actions.
- A training example is formed by sampling a temporal window, the active intent key, the history of prior actions, and the target next `(action_key, arguments)`.

Online / on-policy collection can be added later.

### 4.7 Runtime Owner

**Policy Wrapper**

Responsibilities:
1. Own the image carousel (pre-process + ring buffer + stride).
2. Own the action-history buffer.
3. Hold the current intent key.
4. Call the pure policy with the three inputs.
5. Translate `(action_key, arguments)` into a concrete `fluxCore` action and execute it.
6. Apply any post-model humanization (micro-jitter, reaction delays) here, not inside the model.

**Emitter compatibility:** The wrapper subscribes to the existing `SCRCPYEmitter` `ON_FRAME` event. `Frame.decode` already yields tensors. No modification of the emitter is required for the policy contract.

### 4.8 Architecture Candidate

A previous `SemanticPredictorPolicy` implementation (MobileNetV3-Small backbone + LSTM temporal fusion + dual projection heads scored against registry embeddings) is under consideration as a starting point.

It must be adapted to the locked contract before use:
- Buffering (`_frameFeatures` deque, `addFrame`) must move out of the model into the Policy Wrapper (FR-3).
- The second head currently assumes a discrete parameter registry; the locked design requires a **variant argument** (box / coordinate / key / text), which implies regression or a typed structured head rather than pure cosine-similarity over a parameter embedding table.
- Input resolution 24×24×3 is far below the 224×224 regime MobileNetV3-Small was trained on; backbone choice or adaptation needs explicit validation.
- Intent and action keys must be turned into embeddings by a defined encoding strategy (still open).

## 5. Remaining Open Items

The following items are still undecided and must be resolved before implementation can begin:

- Concrete dtype and value range of the 24×24×3 internal tensor (e.g. float32 in [0, 1] or ImageNet-normalized).
- Exact embedding / encoding strategy for the intent key and for the discrete action keys.
- Concrete value of history length *M* and the padding/masking convention.
- Full formal schema (including type tags) for the variant argument object that the model will emit, and how the second head will produce it (regression vs. discrete parameter registry vs. hybrid).
- Detailed recorded-data file format (how video and the timestamped action log are stored and aligned).
- Final decision on network architecture (adapt the candidate `SemanticPredictorPolicy` or design a new one) and training hyper-parameters.
- Package location under `src/` and the corresponding documentation mirroring path.
