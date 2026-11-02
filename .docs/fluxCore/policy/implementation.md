# Implementation Details

**Source of truth:** `src/fluxCore/policy/`.

## 1. Architecture Overview

```text
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

Entry points: `DCPolicy` for the live step, `DCPolicyCore` if the caller already has stacks.

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

`stackSize` and `frameSize` travel inside `OPTIONS` because they are `PolicyOptions` properties.

## 4. Not implemented in this package

The prior design draft described these. The code does not:

- L2 stateful switch or `stateReset`
- Inference-time noise switch
- `step()` / Executor / intent hierarchy
- Vocabulary lookup inside `forward`
