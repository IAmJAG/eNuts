# Hybrid Discrete–Continuous Policy — Implementation Document

**Status:** Implementation specification (sections 1–13)  
**Source of truth:** `.docs/fluxCore/policy/design.md` and `.docs/fluxCore/policy/term-store.md`. This document translates agreed decisions into implementation guidance. It does not supersede them. Anomaly vs design/term store must be resolved in favor of design/term store unless explicitly amended there.

**Document structure:**

1. Architecture and component responsibilities
2. Class and module design
3. Public APIs and method contracts
4. Data structures and tensor contracts
5. L1 implementation
6. L2 implementation
7. Vocabulary and encoding implementation
8. Intent Hierarchy and action-specific Executors
9. Step orchestration and execution lifecycle
10. State management and reset behavior
11. Error handling and validation
12. Testing strategy
13. Deferred implementation decisions

---

# Section 1 — Architecture and Component Responsibilities

## 1.1 Purpose

This section establishes the implementation-level architecture of the eNuts Policy. It identifies the major components, their responsibilities, and the data flow between them.

The policy is organized around two cooperating layers:

- **L1 — History / Context Buffer**
- **L2 — Policy Core**

The policy's action execution is performed by action-specific **Executor** implementations. The complete interaction cycle is orchestrated by `step()`; `step()` is not assumed to be a method of L2 or of any other particular class.

The implementation will use the technology choices already agreed in the Revised Policy Design. This section references those choices but does not redefine them.

## 1.2 Architectural overview

```text
                    Current observation and context
                 (image, active intent, previously
                   executed action and parameters)
                                  |
                                  v
                 +--------------------------------+
                 | L1: History / Context Buffer   |
                 | - Prepare image                |
                 | - Encode intent/action/params  |
                 | - Maintain circular history    |
                 | - Pad warm-up history          |
                 | - Materialize Layout 3 stacks  |
                 +--------------------------------+
                                  |
                                  | Layout 3:
                                  | intent_stack, image_stack,
                                  | action_stack, parameter_stack
                                  v
                 +--------------------------------+
                 | L2: Policy Core                |
                 | - Process temporal context     |
                 | - Optional recurrent state     |
                 | - Predict discrete action      |
                 | - Predict action parameters    |
                 +--------------------------------+
                                  |
                                  v
                 +--------------------------------+
                 | Action-specific Executor       |
                 +--------------------------------+
                                  |
                                  v
                        Environment / caller → next step
```

`step()` coordinates: accept input → update/obtain L1 history → L2 `forward()` → invoke Executor for the predicted action.

## 1.3 Component responsibilities

### 1.3.1 L1 — History / Context Buffer

**Primary responsibility:** Maintain observation-aligned history and provide L2 with Layout 3 tensors.

L1 always owns **buffer state**. Responsibilities: accept image, active intent, previous_action, previous_parameters; prepare images once; encode discrete/structured context (description excluded); circular history of `stackSize`; warm-up empty/zero pads; materialize Layout 3.

Slot: `(intent_t, image_t_prepared, previous_action_t, previous_parameters_t)` — previously executed controls accompanying the current observation.

**L1 does not predict or execute actions.**

### 1.3.2 L2 — Policy Core

**Primary responsibility:** Consume Layout 3 and predict next action and predicted parameters.

Responsibilities: receive four stacks; within-pass temporal processing; optional recurrent state (default Off) and `stateReset()`; hybrid discrete + continuous heads; active intent as primary blanket while using `intent_stack` history.

**L2 does not own L1 history or execute actions.**

### 1.3.3 Action-specific Executors

Execute predicted action with action parameters. Per-action implementations. Only the `intent_end` Executor applies `pop` / `push` / `replace` to the Intent Hierarchy and may call `stateReset()` at root boundaries.

### 1.3.4 Step orchestration

`step()`: accept observation/context → L1 → `forward()` → Executor. Location of `step()` is not required to be on the model class.

## 1.4 Component relationships and data contracts

**L1 → L2:** `(intent_stack, image_stack, action_stack, parameter_stack)`.

**L2 → Executor:** predicted action + predicted parameters.

**After execution → next L1:** executed action/parameters become previous controls for the next observation.

## 1.5 State ownership

| State | Owner |
|---|---|
| Buffer state | L1 |
| Recurrent state | L2 (optional, default Off) |
| Intent Hierarchy | Not assigned by design; `intent_end` Executor interacts |
| Training state | Training/checkpoint process |

## 1.6 Agreed technology context

Python; PyTorch; Pillow; OpenCV; NumPy; JSON; CUDA default with CPU fallback; PyTorch `state_dict` checkpoints with separate inference/training artifacts and JSON config.

## 1.7 Explicitly unresolved in this section

Class decomposition, exact signatures, tensor dtypes/dims, transform details, embedding widths, JSON schemas, hierarchy storage, Executor registry, `step()` home, device API details, library pins — see later sections and Section 13.

---

# Section 2 — Class and Module Design

## 2.1 Package layout (under `src/fluxCore/policy/`)

Proposed modules (names are implementation choices consistent with design roles):

```text
fluxCore/policy/
  __init__.py                 # public exports
  history.py                  # L1 HistoryContextBuffer
  core.py                     # L2 PolicyCore (nn.Module)
  vocabulary.py               # VocabularyItem, Action/Intent/Parameter vocab helpers
  encoding.py                 # Id/options embed+concat fuse; ParameterEncoder
  layout3.py                  # Layout3Stacks named structure / helpers
  executors/
    __init__.py
    base.py                   # Executor protocol / base
    registry.py               # action-Id → Executor lookup
    intent_end.py             # intent_end Executor
  hierarchy.py                # Intent Hierarchy structure (interacted with by intent_end Executor)
  step.py                     # step() orchestration (not required on PolicyCore)
  device.py                   # CUDA-default / CPU-fallback selection
  checkpoint.py               # policy_config.json, policy_inference.pt, policy_training.pt
  options.py                  # PolicyOptions: stackSize, switches, paths
```

Legacy `DCPolicy` paths under the same tree are not the source of truth for this hybrid design.

## 2.2 Primary types

| Type | Role |
|------|------|
| `HistoryContextBuffer` | L1: buffer state, transforms, encode, Layout 3 materialization |
| `PolicyCore` | L2: `forward`, optional recurrent state, `stateReset`, noise switch |
| `VocabularyItem` | `{Id, description, options}` structure |
| `ParameterEncoder` | Learned deterministic map → fixed-width vector |
| `Layout3Stacks` | Tuple/container of the four stacks |
| `Executor` | Protocol: `execute(action, parameters) -> ExecutionResult` |
| `IntentEndExecutor` | Hierarchy ops + conditional `stateReset` |
| `IntentHierarchy` | Root and subsequent intents (not `intent_stack`) |
| `PolicyOptions` | stackSize, stateful switch, inference-noise switch, device prefs |
| `step(...)` | Function or thin orchestrator object |

## 2.3 Ownership rules (implementation)

- Only `HistoryContextBuffer` mutates buffer state.
- Only `PolicyCore` mutates recurrent state; clear only via `stateReset()`.
- Only `IntentEndExecutor` (among Executors) mutates Intent Hierarchy and may call `stateReset()` on root complete/replace.
- `step` must not embed action execution inside `PolicyCore.forward`.

---

# Section 3 — Public APIs and Method Contracts

## 3.1 HistoryContextBuffer (L1)

```text
__init__(options, image_transform, intent_encoder, action_encoder, parameter_encoder, device)
accept(image, intent, previous_action, previous_parameters) -> None
  # push one slot; drop oldest if full; pads handled on materialize
layout3() -> Layout3Stacks
  # always length stackSize (warm-up padded)
clear_buffer() -> None
  # optional utility; not the same as L2 stateReset
```

Inputs use term-store names: `previous_action`, `previous_parameters`, active `intent`.

## 3.2 PolicyCore (L2)

```text
__init__(options, ..., stateful: bool = False, inference_noise: bool = False)
forward(layout3: Layout3Stacks, active_intent: VocabularyItem | encoded) -> (action, predicted_parameters)
stateReset() -> None
  # no-op if stateful is Off; clears recurrent state if On
set_stateful(enabled: bool) -> None
set_inference_noise(enabled: bool) -> None
```

`forward` must not accept a reset flag. `stateReset` is a separate method.

## 3.3 step orchestration

```text
step(
  observation_image,
  active_intent,
  previous_action,
  previous_parameters,
  *,
  history: HistoryContextBuffer,
  core: PolicyCore,
  executor_registry,
  intent_hierarchy,  # available to intent_end Executor
) -> StepResult
```

Behavior: `history.accept(...)` → `core.forward(history.layout3(), ...)` → resolve Executor by action Id → `execute`.

## 3.4 Executor

```text
execute(action, parameters, context) -> ExecutionResult
```

`IntentEndExecutor.execute` interprets parameters for `pop` | `push` | `replace`, updates Intent Hierarchy, and on root completion/replacement calls `core.stateReset()` when recurrent state is enabled.

## 3.5 Checkpoint

```text
save_inference(path_config_json, path_pt, core, options, ...)
load_inference(...)
save_training(...)
load_training(...)
```

Align with design artifacts: `policy_config.json`, `policy_inference.pt`, `policy_training.pt`.

---

# Section 4 — Data Structures and Tensor Contracts

## 4.1 Layout 3

Canonical channels (term store):

```text
intent_stack, image_stack, action_stack, parameter_stack
```

Temporal length = `stackSize` ∈ {2, 4, 8, 16, 32, 64, 128, 256}.

Semantic content:

- `intent_stack` — per-slot intent history encodings
- `image_stack` — prepared images
- `action_stack` — encodings of previously executed actions
- `parameter_stack` — fixed-width encodings of previously executed parameters

## 4.2 Vocabulary item

```text
{ "Id": str, "description": str, "options": list | dict }
```

`description` never enters tensors or loss.

## 4.3 Prediction output

- Discrete **action** identity (Id) suitable for Executor registry lookup (includes `intent_end`).
- **Predicted parameters** structured for the Executor (for `intent_end`: operation in `pop`|`push`|`replace` plus any payload needed for push/replace).

## 4.4 Implementation defaults vs deferred

Exact dtypes, `D_id`, `D_opt`, image tensor shapes, and pad fill values are **Section 13** unless fixed by a later amendment. Implementation must still guarantee: fixed widths for stacked channels; warm-up length `stackSize`; deterministic parameter encoding.

---

# Section 5 — L1 Implementation

## 5.1 Accept path

1. Validate/normalize inputs (image, active intent, previous_action, previous_parameters or pads).
2. Apply image transform once; store prepared image in modality array.
3. Encode intent (Id∥options → concat fuse).
4. Encode previous_action the same way.
5. Encode previous_parameters via `ParameterEncoder` (deterministic, fixed width).
6. Append to circular modality arrays; if length > `stackSize`, drop oldest.

## 5.2 Materialize Layout 3

- Stack modality arrays along time.
- If length < `stackSize`, pad with empty/zero tensors per design (exact pad side deferred to Section 13; behavior must be consistent).
- Return `Layout3Stacks` without re-transforming images.

## 5.3 Constraints

- No prediction, no Executor calls, no Intent Hierarchy mutation.
- Buffer state independent of L2 stateful switch.

---

# Section 6 — L2 Implementation

## 6.1 Forward path

1. Unpack Layout 3.
2. Within-pass temporal processing over `stackSize` (allowed when stateful Off or On).
3. Condition strongly on **active intent** blanket; still consume `intent_stack`.
4. Discrete head → next action (cosine / classification over action vocab).
5. Continuous / structured heads → predicted parameters.
6. If inference-noise On: stochastic decode; if Off: deterministic (`argmax` / mean).
7. If stateful On: update recurrent state for next call; if Off: no cross-call state.

## 6.2 stateReset

- Clears recurrent state only.
- No-op when stateful Off.
- Does not clear L1 buffer state.

## 6.3 Constraints

- No image transform ownership.
- No Executor execution inside `forward`.
- Encoders for Id/options remain deterministic regardless of inference-noise switch.

---

# Section 7 — Vocabulary and Encoding Implementation

## 7.1 Vocabulary storage

Injectable JSON vocabularies for actions, intents, and parameter-type catalogs as needed. Not static closed sets in code.

## 7.2 Id and options embedding

Per design:

```text
emb_id  = Embed(Id)           # fixed D_id
emb_opt = Encode(options)     # fixed D_opt; zeros if empty
emb     = concat(emb_id, emb_opt)   # default fusion
```

## 7.3 Parameter encoder

Fully learned, deterministic, fixed output width for `parameter_stack`. Variable parameter structure allowed at input; width fixed at output.

## 7.4 intent_end

Registered as an action Id. Parameters carry operation: `pop`, `push`, or `replace` (not separate actions).

---

# Section 8 — Intent Hierarchy and Action-Specific Executors

## 8.1 Intent Hierarchy

- Distinct from `intent_stack`.
- Root intent = first pushed, overarching.
- Subsequent intents are sub-intents under the root.
- Storage owner not mandated by design; must be reachable by `IntentEndExecutor`.

## 8.2 Executor registry

Map action Id → Executor instance. Unknown action Id is an error (Section 11).

## 8.3 IntentEndExecutor

1. Read operation from action parameters (`pop`|`push`|`replace`).
2. Apply to Intent Hierarchy.
3. If root completed or replaced and L2 stateful On → `policy_core.stateReset()`.
4. Sub-intent pop alone does not require `stateReset`.

## 8.4 Other Executors

Perform domain execution only; no hierarchy or `stateReset` unless a future design amendment says otherwise.

---

# Section 9 — Step Orchestration and Execution Lifecycle

## 9.1 Single step

1. Receive image, active intent, previous_action, previous_parameters.
2. `history.accept(...)`.
3. `layout3 = history.layout3()`.
4. `action, predicted_parameters = core.forward(layout3, active_intent)`.
5. `executor = registry.get(action.Id)`.
6. `executor.execute(action, predicted_parameters, context)`.
7. Caller supplies executed action/parameters as previous controls on the **next** observation.

## 9.2 Episode / task boundary

Orchestration or training loop calls `core.stateReset()` at episode/task end (and major root boundaries via `IntentEndExecutor` as designed).

## 9.3 Training alignment

Reset cadence matches inference: episode boundary + major (root) intent change/completion — not every step.

---

# Section 10 — State Management and Reset Behavior

| Mechanism | Clears | Caller |
|-----------|--------|--------|
| L1 circular eviction | Oldest slots only | automatic on accept |
| L1 `clear_buffer` (if provided) | Buffer state | explicit, rare |
| `PolicyCore.stateReset()` | Recurrent state only | `IntentEndExecutor` at root boundary; orchestration at episode boundary; training at matching points |
| Stateful Off | N/A | `stateReset` no-op |

Do not conflate buffer state with recurrent state.

---

# Section 11 — Error Handling and Validation

Implementation should validate at boundaries:

- `stackSize` not in allowed set → reject at options construction.
- Missing required vocab Id → fail encode or registry lookup clearly.
- Layout 3 temporal dimension ≠ `stackSize` → fail before `forward`.
- Unknown action Id in registry → fail before execute.
- `intent_end` with invalid operation parameter → fail in `IntentEndExecutor`.
- CUDA unavailable → fall back to CPU per design; do not assume GPU exists.

Prefer explicit exceptions over silent pads beyond designed warm-up pads.

---

# Section 12 — Testing Strategy

| Layer | Focus |
|-------|--------|
| L1 | Circular eviction; warm-up length; no double image transform; Layout 3 names/meanings; pad vs real slots |
| Encoding | description never in tensors; concat fuse shapes; parameter encoder determinism |
| L2 | forward deterministic with noise Off; noise On changes discrete sampling path; `stateReset` no-op when Off; recurrent differs across calls only when On |
| step | order accept → forward → execute; previous controls feedback |
| intent_end | pop/push/replace; stateReset only on root complete/replace when stateful On |
| Checkpoint | inference load without optimizer; training resume fields present |

Use term-store names in test descriptions.

---

# Section 13 — Deferred Implementation Decisions

These remain open until fixed here or in design; they must not be treated as silent defaults that conflict with design:

1. Exact `D_id`, `D_opt`, backbone widths, feature dimensions.
2. Exact image transform pipeline (resize, normalize constants) and pad side (left/right) for warm-up.
3. Tensor dtypes and concrete zero/empty pad values.
4. Fine-grained Intent Hierarchy storage API and push payload schema.
5. Concrete temperature/noise schedules when inference-noise is On.
6. Multi-env batching details for `stateReset` masks.
7. Exact `step()` hosting (module-level function vs orchestrator class).
8. Executor registration style (explicit registry vs entry points).
9. Device-selection API surface and multi-CUDA behavior.
10. Library version pins.
11. JSON schemas for vocabularies and `policy_config.json`.
12. Whether active intent is passed into `forward` as structured item, Id-only, or encoded tensor (design requires active intent as blanket; encoding form is implementation detail).

---

**End of implementation document.**
