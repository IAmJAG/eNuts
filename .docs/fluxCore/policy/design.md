# Hybrid Discrete–Continuous Policy — Design Draft

**Status:** Active design (clean slate). Archived prior docs under `.docs/_archive/fluxCore/policy/` are reference only.

**Terminology:** See `.docs/fluxCore/policy/term-store.md` for agreed terms and rules.

---

## Overall shape

Two cooperating layers:

| Layer | Working name | Role |
|-------|----------------|------|
| **L1** | **History / Context Buffer** | Ingests the live observation + control signals, maintains a fixed-length circular history, and emits a tensor-ready stack of length `stackSize`. |
| **L2** | **Policy Core** | Consumes the fixed-size tensor stack from L1 and produces the next discrete action + predicted parameters (hybrid output). |

L1 is always stateful (owns the circular buffer). This persistent L1 data is the **buffer state**.  
L2 is **optionally stateful** via an explicit switch (default **Off**). When enabled, L2 may maintain **recurrent state** across forward passes.

## Step, `forward()`, and execution (locked)

A **step** is one complete policy interaction cycle:

1. Accept the current input: the observation and its associated context.
2. Update or obtain the required L1 history for that input.
3. Call the model's `forward()` method.
4. Receive the predicted action and its parameters.
5. Execute the predicted action through its associated Executor implementation.

The next observation begins the next step.

**`step()`** is the operation that accepts the input, calls `forward()`, and executes the resulting action. It represents the interaction-cycle orchestration and does not necessarily belong inside the model class; it may be implemented as an independent function or by another orchestration component.

**`forward()`** is the model method that processes its supplied input and predicts/produces an action and its parameters. It does not, by itself, define the complete interaction cycle and does not necessarily execute the action.

**Execution** is the carrying out of the predicted action by its associated Executor implementation.

---

## Layer 1 — History / Context Buffer

**Inputs on each step**

- `image` — current raw frame
- `intent` — active intent (structured vocabulary item; see Vocabulary)
- `previous_action` — previously executed action accompanying the current observation (or pad)
- `previous_parameters` — parameters accompanying that previously executed action and the current observation (or pad / empty)

**Responsibilities**

1. **Image preparation**  
   Own the visual transform pipeline (resize, normalize, etc.) so that what enters the buffer is already in the form the model expects.

2. **Parameter / discrete encoding**  
   Convert intent, action, and parameters into tensor-friendly representations using the vocabulary base format. Description fields are never included in computation.

3. **Circular buffer**  
   Maintain a fixed-length history of length `stackSize`. On each accepted step:
   - push the new prepared slot,
   - drop the oldest slot when full.

4. **Internal storage form**  
   Keep **arrays per modality**, already in final-ready form (e.g. transformed images). No further back-processing is required when materializing the L1→L2 contract.

5. **Tensorization (Layout 3)**  
   At the boundary to L2, emit:

   ```text
   (intent_stack, image_stack, action_stack, parameter_stack)
   ```

   where each element is an already-stacked tensor of length `stackSize`.

**What a “slot” conceptually holds**

Each historical entry is a 4-tuple:

```text
(intent_t, image_t_prepared, previous_action_t, previous_parameters_t)
```

**Slot temporal alignment (locked)**

`previous_action_t` / `previous_parameters_t` are the **previously executed controls accompanying the current observation** represented by `image_t_prepared`.

The phrase **“action taken from this image”** refers to the action context recorded alongside that image: the action had already been executed before the current observation was received. It does **not** mean the action selected after observing that image, and it does not mean the action that produced the image. L2 receives this previous-control context and predicts the **next** action and its parameters.

**Buffer state and buffer semantics**

The **buffer state** is the persistent history maintained by L1's circular buffer. It consists of the buffered per-modality entries represented at the L1 → L2 boundary by the Layout 3 stacks. It is maintained across accepted input steps, independently of whether L2 recurrent state is enabled.

- Capacity = `stackSize` ∈ {2, 4, 8, 16, 32, 64, 128, 256}.
- Strict circular: always length ≤ `stackSize`; once full, every push drops the oldest.
- **Warm-up:** pad missing slots with **empty / zero tensors** so the emitted stacks are always length `stackSize`.
- Pads for missing action/parameters are explicit, not omitted channels.

**Parameter packing (locked)**

Parameters are dynamic. Encoding uses a **fully learned encoder** that maps the structured parameter object → fixed-size vector for `parameter_stack`.

- The encoder itself is **deterministic** (same parameter input → same vector). This keeps stacks stable and training reproducible.
- Variable structure is absorbed by the encoder; the **output width is fixed** so Layout 3 stacking works.
- Preventing “exact previous parameters → exact next parameters” is **not** done by making the encoder noisy. It is a property of the full decision context and of optional stochasticity on the **policy outputs** at inference time.

**Output of L1**

Layout 3 tensor stacks, always of length `stackSize` (padded while warming up).

---

## Tensor layout (L1 → L2) — locked

**Layout 3** is the contract:

```text
tuple(
  intent_stack,   # stacked tensor from array of intents
  image_stack,    # stacked tensor from array of prepared images
  action_stack,   # stacked tensor from array of previously executed actions
  parameter_stack,    # stacked tensor from array of their previously executed parameters
)
```

L1 may keep modality arrays internally; conversion to these stacked tensors occurs only at the hand-off to L2.

---

## Intent handling (blanket + mid-history change)

**Locked preference:** Intent is conceptually a **blanket** over the decision being made *now*. The intent governing that decision is the **active intent**.

**Practical rule for the buffer**

- L1 records the intent that was active at each step in the per-slot temporal history, producing the `intent_stack` tensor channel.
- At prediction time, the **active** intent is the primary conditioning signal (blanket).
- If intent changes within the history window:
  - Older slots keep the intent that was active when they were written.
  - The model can therefore *see* that a change occurred (via `intent_stack`).
  - The decision itself is still framed as “under the **active** intent.”

So: **intent history exists; the active intent is special.**

**Active intent and root intent (terminology locked)**

- **Active intent** is the intent currently governing the policy decision.
- **Root intent** is the first intent pushed: the ultimate, overarching intent above the subsequent intents.
- The active intent may be the root intent or a subsequent intent. The design must make explicit whether the active intent is the root intent.
- **Intent history** is the sequence of intents associated with the observations in the history window. Each slot retains the intent that was active when that slot was written.

### Major intent and `intent_end` (locked)

Intents may compose hierarchically (sub-intents under a root). This hierarchical organization is the **Intent Hierarchy**. It is distinct from the temporal `intent_stack` tensor channel produced by L1 and received by L2.

| Concept | Role |
|---------|------|
| **Major (root) intent** | The first intent pushed and the overarching intent at the top of the Intent Hierarchy; finishing it ends the task for reset purposes |
| **Sub-intents** | Pushed under the root within the Intent Hierarchy; each is expected to end via an `intent_end` action |
| **`intent_end` action** | Discrete action the policy may emit; its parameters specify the operation (`pop`, `replace`, or `push`) to apply to the Intent Hierarchy |

L2 internal-state reset (when the stateful switch is On) is triggered by **root** completion or **root** replacement — not by every sub-intent pop. The Executor implementation associated with `intent_end` invokes L2's **`stateReset()` method** at those root boundaries. The training loop applies the corresponding reset at matching training boundaries. The Executor associated with `intent_end` handles the action's Intent Hierarchy operation; this does not make Intent Hierarchy management a responsibility of every Executor.

---

## Layer 2 — Policy Core

**Input**

- The four Layout-3 stacks produced by L1 (each length `stackSize`).

**Responsibilities (high level)**

- Consume the historical context (visuals + intents + previously executed actions + their parameters).
- Produce a **hybrid** decision:
  - **Discrete** head(s): next action (including `intent_end` when appropriate) via classification / cosine-over-vocabulary style.
  - **Continuous** head(s): spatial / geometric / other open action parameters via regression.

**Action execution and Executor implementations**

L2 predicts the next action and its parameters. An **Executor** accepts an action and its parameters and carries out that action. Each action may have its own Executor implementation, so execution behavior is action-specific. The Executor associated with `intent_end` may apply the action's `pop`, `replace`, or `push` parameters to the Intent Hierarchy and invoke L2's `stateReset()` method when a root-intent boundary is reached. This responsibility is specific to the `intent_end` Executor; it is not a responsibility shared by every Executor.

**L2 temporal processing and recurrent state (locked)**

The L1 buffer state and L2 recurrent state are distinct state concepts owned by different layers.

- **Buffer state** is the persistent history owned by L1's History / Context Buffer. It is represented to L2 by the fixed-length Layout 3 stacks.
- **Recurrent state** is optional internal state owned by L2 and carried across separate forward passes.
- **Within-pass temporal processing** is L2's processing of the history supplied in the current L1 stacks. It does not, by itself, make L2 stateful across calls.

| L2 statefulness switch | Behaviour |
|--------|-----------|
| **Off** (**default; stateless L2**) | L2 has no persistent recurrent state across calls. All history that influences the decision across steps is supplied by the L1 buffer state. Within one forward pass, any temporal operator over the supplied stack is allowed (attention, an LSTM unrolled over `stackSize`, mean-pooling, etc.). |
| **On** (**stateful L2**) | L2 may carry internal recurrent state (e.g. LSTM/GRU hidden state) that persists between forward passes, enabling context beyond the L1 history window of `stackSize`. |

**Reset (locked) — method, not state**

Reset is an explicit **method** on L2 named **`stateReset()`**, not a flag or argument on `forward`.

| Caller | When to invoke |
|--------|----------------|
| **Inference / `intent_end` Executor** | On **major (root) intent** change or completion. The Executor implementation associated with `intent_end` invokes `stateReset()` at those root boundaries. The inference caller/orchestration also invokes `stateReset()` on episode / task boundary. |
| **Training** | **Match inference**: call `stateReset()` on episode boundary and on major intent change (per-env in batched training). Do **not** call reset every step. |

When the stateful switch is **Off**, the method is a no-op because L2 has no persistent recurrent state.  
When **On**, the method clears L2 recurrent state so the next forward starts clean.

**Inference-time noise switch (locked)**

| Switch | Behaviour |
|--------|-----------|
| **Off** (**default**) | Deterministic decode (`argmax` / mean continuous outputs). |
| **On** | Stochastic decode (e.g. temperature sampling on discrete heads; optional noise on continuous heads). |

Independent of the L2 stateful switch. Param / Id encoders remain deterministic regardless of this switch.

**What L2 does *not* own**

- Circular buffer / history bookkeeping (L1).
- Raw image transforms (L1).
- Action execution and action-specific Executor implementations — L2 predicts actions and parameters; the corresponding Executor implementation executes them. The `intent_end` Executor may apply its parameters to the Intent Hierarchy.
- Long-term persistence of the L1 carousel across process restarts (unless later decided).

---

## Vocabulary base format (locked)

All discrete vocabulary items share this structure:

```text
{
  Id:          <text> / <label> / <name>,     # stable identity
  description: <human-readable text>,         # NEVER used in computation
  options:     <array | dictionary>           # open-ended; may affect embedding
}
```

### Action

- **Id** — fixed text/label of the action. Immutable for a given entry. Used to compute the embedding **deterministically**.
- **options** — open-ended; may describe parameter type or related hints. Encoded and fused with Id (see below).
- **description** — documentation only; excluded from computation.
- Special action **`intent_end`** — its parameters specify the operation (`pop`, `replace`, or `push`) to apply to the Intent Hierarchy. The Intent Hierarchy is distinct from the temporal `intent_stack` tensor channel.

### Parameters

- **Id** — type of the parameter (e.g. `Key`, `tap`, `box`).
- **options** — the value(s) (e.g. `[ESCAPE]`, `[0.254, 0.586]`).
- Encoded by the **fully learned parameter encoder** (deterministic, fixed output width). Description does not participate.

**Parameter lifecycle terminology**

- **Predicted parameters** are the parameters produced by L2 for its predicted next action.
- **Action parameters** are the parameters associated with an action and interpreted by the executor.
- **Previously executed parameters** are the parameters accompanying an already executed action and the current observation in L1 history.

These terms describe the same general parameter concept at different stages of the action lifecycle; they do not define separate parameter types.

### Intent

Same base shape. Hierarchy is expressed **inside** the intent item via `options` (or hierarchical Ids), **not** as an extra top-level argument. The **Intent Hierarchy** describes the root intent and subsequent pushed intents. It is distinct from `intent_stack`, which is the temporal history tensor channel produced by L1 and received by L2. The model sees the active intent as the blanket plus per-slot intent history.

Vocabularies remain **injectable** (not static). Placeholders are used until concrete sets are supplied.

### Id vs options embedding (locked)

For Action and Intent:

```text
emb_id  = Embed(Id)              # fixed width D_id
emb_opt = Encode(options)        # fixed width D_opt (zeros if empty);
                                 # learned encoder absorbs variable option structure
emb     = Fuse(emb_id, emb_opt)  # default: concat → width D_id + D_opt
```

- **Separate vectors, then fuse** — locked.
- **Default fusion operator: concat.**
- Variable option *content* does not imply variable embedding *length*; encoders always emit fixed-width vectors so Layout 3 and batching stay valid.
- Exact values of `D_id` / `D_opt` are left to implementation details.

---

## Data-flow sketch

```text
                    ┌─────────────────────────────────────┐
 current image ────►│                                     │
 active intent ────►│  L1  History / Context Buffer       │
 previously        │                                     │
 executed action ──►│   • transform image                 │
 previously        │                                     │
 executed params ──►│   • encode intent/action (Id∥opt)   │
                    │   • learned param encoder (det.)    │
                    │   • circular arrays (final-ready)   │
                    │   • pad to stackSize if needed      │
                    │   • emit Layout-3 tensor stacks     │
                    └──────────────────┬──────────────────┘
                                       │ (intent, image, previous-action,
                                       │  previous-parameter) stacks
                                       ▼
                    ┌─────────────────────────────────────┐
                    │  L2  Policy Core                    │
                    │   • stateful switch: off (default)  │
                    │                      | on           │
                    │   • stateReset() method (not a flag)│
                    │   • inference noise: off (default)  │
                    │                      | on           │
                    │   • temporal / context fusion       │
                    │   • discrete head(s) incl. intent_end│
                    │   • continuous head(s)              │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                         next action + predicted parameters
                              (the corresponding action-specific
                               Executor executes the action; the
                               `intent_end` Executor may update the
                               Intent Hierarchy and stateReset L2 at root boundaries)
```

After execution, the caller (or a thin wrapper) feeds the **executed action and its parameters** back as the next step’s `previous_action` / `previous_parameters`. These are the previously executed controls accompanying the next current observation.

---

## Locked decisions summary

| Topic | Decision |
|-------|----------|
| Step | Complete policy interaction cycle: accept input, update/obtain L1 history, call `forward()`, receive predicted action and parameters, then execute through the associated Executor |
| `step()` | Orchestrates the complete interaction cycle; does not necessarily belong inside the model class |
| `forward()` | Model method that processes supplied input and predicts/produces an action and parameters; does not necessarily execute the action |
| Execution | Carrying out the predicted action through its associated Executor implementation |
| L1 → L2 contract | **Tensor Layout 3** |
| L1 internal storage | Arrays per modality, already final-ready |
| Warm-up | Pad with empty / zero tensors → always length `stackSize` |
| `stackSize` | ∈ {2, 4, 8, 16, 32, 64, 128, 256} |
| Slot temporal alignment | **Previously executed controls accompanying the current observation** |
| Buffer state | Persistent circular history owned by L1; supplied to L2 as Layout 3 stacks |
| L2 recurrent state | Optional persistent internal state across forward passes; Off by default |
| L2 within-pass temporal processing | Allowed whether the L2 statefulness switch is Off or On; processing the supplied L1 stack does not itself imply recurrent state |
| L2 stateful switch | **Off by default**; On = carry internal recurrent state |
| L2 state reset | **Method** (`stateReset()`), not a forward flag; call on major (root) intent change/completion and episode boundary; training matches inference |
| Intent Hierarchy | Root intent and subsequent pushed intents; `intent_end` parameters specify **pop**, **replace**, or **push** operations |
| `intent_stack` | Temporal history tensor channel produced by L1 and received by L2 |
| Action execution | Each action may have its own Executor implementation; the `intent_end` Executor may interact with the Intent Hierarchy and invoke L2 `stateReset()` at root boundaries |
| Inference-time noise | **Switch on/off**, **default Off** (deterministic decode) |
| Intent | Active intent is the blanket for the current decision; per-slot intent history in `intent_stack` |
| Vocabulary base | `{ Id, description, options }` — description never in computation |
| Action Id | Fixed; drives deterministic embedding |
| Parameters | Id = type, options = value(s); **fully learned encoder (deterministic, fixed width)** |
| Id vs options embedding | **Separate vectors, then fuse**; **default fusion = concat** |
| Intent specialization | Nested/hierarchical **options** (or hierarchical Id), not a new top-level argument |
| Discrete vocabularies | Injectable / not static; placeholders until supplied |
| Non-copying of params | Full context + optional output stochasticity; **not** noisy param encoding |

---

## Technology decisions

Technology choices are recorded here as part of the design so that the implementation document can specify how the selected technologies realize the architecture. The implementation document must not silently introduce or change these choices.

| Technology area | Decision | Status / scope |
|-----------------|----------|----------------|
| Programming language | **Python** | **Agreed.** The eNuts Policy implementation will be written in Python and will follow the project's Naming Conventions and Coding Style documents. |
| Deep learning framework | **PyTorch** | **Agreed.** PyTorch is the primary deep learning framework for the policy implementation, including model components, tensor operations, automatic differentiation, training, and inference. The specific PyTorch version and deployment configuration remain to be selected. |
| Image processing / computer vision | **Pillow and OpenCV** | **Agreed.** Both libraries will be used according to the operation and data representation best suited to each task. Pillow supports image loading and PIL-image workflows; OpenCV provides computer-vision and image-processing operations. They are complementary rather than mutually exclusive alternatives. |
| Numerical and array processing | **NumPy** | **Agreed.** NumPy will be used for numerical operations and processing of `ndarray` data, including array-based workflows that interoperate with OpenCV. |
| Tensor processing | **PyTorch tensor facilities** | **Agreed.** PyTorch tensors are the primary tensor representation used by the policy model and its learning/inference pipeline. Conversion between PIL images, NumPy arrays, and PyTorch tensors will occur where required by the processing pipeline. |
| Model serialization / checkpoint format | **PyTorch `state_dict`-based checkpoints, with separate inference and training artifacts** | **Agreed.** Save learned model parameters using PyTorch state dictionaries rather than serializing complete model objects. Keep human-readable model configuration in JSON. Maintain separate inference and resumable-training checkpoint files. |
| Configuration and vocabulary storage formats | **JSON** | **Agreed.** JSON will be used for human-readable configuration and vocabulary data. The precise schemas, validation rules, and loading APIs remain to be specified in the implementation document. |
| Hardware acceleration / execution environment | **CUDA GPU by default, with an explicit CPU fallback** | **Agreed.** The implementation will check CUDA availability explicitly and use a CUDA device by default when available. CPU execution must remain available as a fallback when CUDA is unavailable or cannot be used. |

**Model serialization and checkpoint decision scope**

Three artifacts are defined by purpose:

- `policy_config.json` — model architecture/configuration and the metadata required to reconstruct the model.
- `policy_inference.pt` — model state dictionary and inference-related metadata required to load the policy for inference.
- `policy_training.pt` — a resumable training checkpoint containing the model state dictionary and the training state required to resume.

---

## Deferred to implementation details

The following are **not** design locks. They must be specified when **implementation details** (and related requirement / implementation docs) are created:

1. Exact embedding dimensions (`D_id`, `D_opt`, backbone / feature widths).
2. Fine-grained behavior of the `intent_end` Executor for applying pop, replace, or push parameters to the Intent Hierarchy.
3. Concrete temperature / noise schedules when inference-time noise is On.
4. Precise API signature of L2 `stateReset()` (return value, multi-env behaviour).
5. Placeholder tensor dtypes and concrete warm-up pad values.

---

## Design principles

- Clear **separation of concerns**: L1 = history + tensorization; L2 = decision; each action is executed by its associated Executor implementation.
- A **step** is the complete interaction cycle; `forward()` performs model prediction, while execution is performed by the associated Executor.
- **Circular buffer** of fixed, power-of-two-friendly `stackSize`.
- History contains **intent + prepared image + previously executed controls accompanying the current observation**.
- Hybrid output (discrete + continuous) lives in L2.
- L1 buffer state and L2 recurrent state are distinct; L1 always maintains its circular history, while L2 recurrent state is optional (default Off).
- L2 may perform temporal processing over the supplied L1 history within a single forward pass even when recurrent state is Off.
- L2 internal-state **`stateReset()` is a method**, invoked by the `intent_end` Executor at root-intent boundaries or by the training loop at matching training boundaries — not a per-step state flag.
- Variable structure in options/parameters is handled by **learned encoders with fixed output width**.
- Vocabularies are structured, injectable, and free of hard-coded closed sets.
- Human-readable `description` never enters the computation graph.
