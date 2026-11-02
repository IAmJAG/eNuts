# Requirements & Design Specifications

**Source of truth:** `src/fluxCore/policy/`.

## 1. Project Overview

`fluxCore.policy` is a two-layer hybrid discrete-continuous policy.

- **L1 `DCPolicy`** transforms the current image, keeps a fixed-length circular history of intent / image / action / parameter tensors, pads to `stackSize`, and calls L2.
- **L2 `DCPolicyCore`** runs a visual backbone, merges visual features with history embeddings, blankets the result with the active intent, and emits three heads: `ACTION`, `PARAMETERKIND`, `SPATIAL`.

Vocabulary types exist and are not wired into `forward`.

## 2. Functional Requirements

- **FR-1:** `DCPolicy.forward` accepts `activeIntent`, `previousIntent`, a PIL `image`, `previousAction`, and `previousParameters`.
- **FR-2:** The image is resized to `frameSize`, converted to a tensor, and ImageNet-normalized before it enters the buffer.
- **FR-3:** History is four circular deques (`_intents`, `_frames`, `_actions`, `_parameters`) of length `stackSize`.
- **FR-4:** Each step appends the previous intent, the transformed image, the previous action, and the previous parameters.
- **FR-5:** Emitted stacks are always length `stackSize`. Missing slots are zero-padded at the front.
- **FR-6:** L2 `forward` accepts `intent`, `intentSpace`, `visualSpace`, `actionSpace`, `parameterSpace`.
- **FR-7:** Visual input is 4D unbatched `[T, C, H, W]` or 5D batched `[B, T, C, H, W]`.
- **FR-8:** History tensors are concatenated with visual features on the last dim, then reduced by a mean over time.
- **FR-9:** The active intent is concatenated with the slot mean (intent blanket) before the heads.
- **FR-10:** Output is a dict with keys `ACTION`, `PARAMETERKIND`, `SPATIAL`. `SPATIAL` is sigmoid-bounded. `forward` is deterministic.
- **FR-11:** `save` writes `VERSION`, `MODELSTATE` (`state_dict`), and `OPTIONS` (`PolicyOptions.encode()`).
- **FR-12:** `load` checks version, requires `MODELSTATE` and `OPTIONS`, builds the class with the options dict, and `load_state_dict(..., strict=True)`.
- **FR-13:** A mismatched backbone fails at `load_state_dict`. Supplying the backbone module is the caller's responsibility.
- **FR-14:** `PolicyOptions` consumes known option keys from `kwargs`. Remaining keys are left for `nn.Module`.
- **FR-15:** `featureDimension` is taken from the backbone. A caller-supplied value is ignored.
- **FR-16:** `stackSize` is an option, default 4. Any integer `>= 1`. Not restricted to a power-of-two set. `DCPolicy` uses it for deque length. `frameSize` is the image resize.

## 3. Non-Functional Requirements

- **NFR-1:** Default backbone is MobileNet V3 Small. Feature width comes from `last_channel` (576).
- **NFR-2:** Default device is `"cuda"`, falling back to CPU when CUDA is unavailable (`getTorchDevice`).
- **NFR-3:** Backbone may be frozen (`freezeBackbone`, default True).
- **NFR-4:** Checkpoint version is `DCPolicyCore.VERSION` (`"0.0.1"`). A different version raises.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: `kwargs` are stripped by `PolicyOptions`
- **Affected Modules:** `src/fluxCore/policy/__policyOption.py`, `src/fluxCore/policy/__dcPolicyCore.py`
- **Description of Standard / Best Practice:** Options and module kwargs are usually separate arguments.
- **Divergence:** `PolicyOptions` pops every `DEFAULTS` key it understands from the shared `kwargs` dict.
- **Design Decision & Justification:** After options are consumed, what remains is intended for `nn.Module`.
- **Code Doc Cross-Reference:** `policyOption.md`, `dcPolicyCore.md`.

### Issue / Item 2: L2 has no recurrent state
- **Affected Modules:** `src/fluxCore/policy/__dcPolicyCore.py`
- **Description of Standard / Best Practice:** A design draft described an L2 stateful switch and `stateReset()`.
- **Divergence:** The code is stateless across calls. History is only the L1 stacks, reduced by a time mean.
- **Design Decision & Justification:** Code is the source of truth. The switch and reset method are not implemented.
- **Code Doc Cross-Reference:** `dcPolicyCore.md`, `implementation.md`.

### Issue / Item 3: Vocabulary is not on the forward path
- **Affected Modules:** `src/fluxCore/policy/vocabulary/`
- **Description of Standard / Best Practice:** Discrete heads often embed against a live vocabulary inside `forward`.
- **Divergence:** `Vocabulary` / `VocabularyItem` exist. `forward` emits raw embedding-sized tensors. Decoding is outside the module.
- **Design Decision & Justification:** Encoding is deterministic (`deterministicEmbedding`). The caller owns the vocab and the decode.
- **Code Doc Cross-Reference:** `vocabulary/vocabulary.md`.

### Issue / Item 4: Inference-time noise is not a policy option
- **Affected Modules:** none in this package
- **Description of Standard / Best Practice:** A design draft put a noise switch on the policy.
- **Divergence:** Noise is not in `PolicyOptions` and is not applied in `forward`.
- **Design Decision & Justification:** Noise is an inference concern. The inference implementation adds it after `forward` if it wants it. Encoders stay deterministic.
- **Code Doc Cross-Reference:** `implementation.md` section 4.
