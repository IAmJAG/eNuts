# Implementation Details

**Source of truth:** `src/fluxCore/policy/`.

## 1. Architecture Overview

```text
Inference  → DCPolicy (L1 + L2)
Training   → DCPolicyCore only

DCPolicy (L1)
  transform image
  append previousIntent / image / previousAction / previousParameters
  pad stacks to stackSize
  → DCPolicyCore.forward

DCPolicyCore (L2)
  backbone(visual) → visualFeatures
  slotMerge(visualFeatures ∥ intentSpace ∥ actionSpace ∥ parameterSpace)
  mean over time
  contextMerge(slotMean ∥ active intent)
  → ACTION, PARAMETERKIND, SPATIAL
```

Inference uses `DCPolicy`. Training uses `DCPolicyCore` with stacks the dataset already built.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/policy/__dcPolicy.py` | `.docs/fluxCore/policy/dcPolicy.md` | L1 buffer and image transform |
| `src/fluxCore/policy/__dcPolicyCore.py` | `.docs/fluxCore/policy/dcPolicyCore.md` | L2 core, heads, save/load |
| `src/fluxCore/policy/__policyOption.py` | `.docs/fluxCore/policy/policyOption.md` | Options consumed from kwargs |
| `src/fluxCore/policy/__utilities.py` | `.docs/fluxCore/policy/utilities.md` | Defaults, backbone builder |
| `src/fluxCore/policy/vocabulary/__vocabulary.py` | `.docs/fluxCore/policy/vocabulary/vocabulary.md` | Vocab list and embedding stack |
| `src/fluxCore/policy/vocabulary/__vocabularyItem.py` | `.docs/fluxCore/policy/vocabulary/vocabularyItem.md` | Id / options embedding |

Public exports from `fluxCore.policy`: `DCPolicy`, `DCPolicyCore`, `PolicyOptions`.

## 3. Core Workflows & Data Flow

### Step (L1)

1. `DCPolicy.forward(activeIntent, previousIntent, image, previousAction, previousParameters)`.
2. Image → resize `frameSize` → tensor → normalize. Move to `self.device`.
3. Append `previousIntent`, image, `previousAction`, `previousParameters` (all on device).
4. `_stack` zero-pads the front until length `stackSize`.
5. `super().forward(activeIntent, intentSpace, visualSpace, actionSpace, parameterSpace)`.

### Core forward (L2)

1. Move all inputs to `self.device`.
2. If `visualSpace` is 5D, flatten `B*T` for the backbone, then reshape back to `[B, T, F]`.
3. If `freezeBackbone`, backbone runs under `torch.no_grad()`.
4. `slotInput = cat(visualFeatures, intentSpace, actionSpace, parameterSpace)` on the last dim.
5. `slotMerge` → mean over time.
6. Active intent is unsqueezed to `[1, I]` if 1D, and expanded to batch if needed.
7. `contextMerge(cat(slotMean, intent))`.
8. Return `{"ACTION": ..., "PARAMETERKIND": ..., "SPATIAL": ...}`.

Widths (defaults): visual `F=576`, intent/action/parameterKind embeddings `128`, spatial output `4`.

`slotMerge` input width = `F + I + A + P`.  
`contextMerge` input width = `F + I`.

`forward` is deterministic. It does not add noise.

### Save / load

`save(path)` writes:

```text
VERSION, MODELSTATE, OPTIONS
```

`load(path, module=None, device="cuda")`:

1. Reject a missing or mismatched `VERSION`.
2. Require `MODELSTATE` and `OPTIONS`.
3. Drop `__type__` from `OPTIONS` and pass the rest as kwargs.
4. `load_state_dict(..., strict=True)`. A different backbone raises here.

`stackSize` and `frameSize` travel inside `OPTIONS` because they are `PolicyOptions` properties. `stackSize` is any integer `>= 1` (default 4). It is not restricted to a power-of-two set.

## 4. Deferred outside this package

### Inference-time noise

Not a `PolicyOptions` item. Not applied inside `forward`.

The heads emit embedding vectors (`ACTION`, `PARAMETERKIND`) and a sigmoid `SPATIAL` in `[0, 1]`. Decode is cosine against the vocabulary, outside this package.

Noise, if used, is added by the inference implementation after `forward` returns:

- Off (default): use the tensors as returned.
- On: add Gaussian noise to the three tensors. Clamp `SPATIAL` back to `[0, 1]`.

Encoders stay deterministic. Training does not see this noise.

### Training stacks

Inference uses `DCPolicy`. Training uses `DCPolicyCore` only.

There is no `stackTime`. Training runs at the video frame rate. No frame is skipped.

The dataset owns matching L1: same transform, same `stackSize`, front zero-pad, same slot alignment (previous controls with the current image), active intent passed separately as the blanket.

Actions are timestamped from 0 (video start) and snapped to the nearest frame.

If several actions share one frame, that frame is repeated once per action, in timestamp order, until none remain:

```text
frame F, actions [A, B, C]
  slot: F + A
  slot: F + B
  slot: F + C
```

A frame with no action is still one slot, with a zero action and zero parameters.

A training sample is one window of `stackSize` slots. The window slides by one slot. The target is the action of the next slot.

## 5. Not implemented in this package

- L2 stateful switch or `stateReset`
- `step()` / Executor / intent hierarchy
- Vocabulary lookup inside `forward`
- `stackTime`
