# Hybrid Discrete–Continuous Policy — Design Draft

**Status:** Active design (clean slate). Archived prior docs under `.docs/_archive/fluxCore/policy/` are reference only.

---

## Overall shape

Two cooperating layers:

| Layer | Working name | Role |
|-------|----------------|------|
| **L1** | **History / Context Buffer** | Ingests the live observation + control signals, maintains a fixed-length circular history, and emits a tensor-ready stack of length `stackSize`. |
| **L2** | **Policy Core** | Consumes the fixed-size tensor stack from L1 and produces the next discrete action + continuous arguments (hybrid output). |

L1 is always stateful (owns the circular buffer).  
L2 is **optionally stateful** via an explicit switch (default **Off**).

---

## Layer 1 — History / Context Buffer

**Inputs on each step**

- `image` — current raw frame  
- `intent` — current intent (structured vocabulary item; see Vocabulary)  
- `previous_action` — action that was last executed (or pad)  
- `previous_parameters` — parameters that accompanied that action (or pad / empty)

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
   (intent_stack, image_stack, action_stack, param_stack)
   ```

   where each element is an already-stacked tensor of length `stackSize`.

**What a “slot” conceptually holds**

Each historical entry is a 4-tuple:

```text
(intent_t, image_t_prepared, action_t, parameters_t)
```

**Slot temporal alignment (locked)**

`action_t` / `parameters_t` mean **action taken from this image** (the decision associated with `image_t`), not the action that produced the image.

**Buffer semantics**

- Capacity = `stackSize` ∈ {2, 4, 8, 16, 32, 64, 128, 256}.
- Strict circular: always length ≤ `stackSize`; once full, every push drops the oldest.
- **Warm-up:** pad missing slots with **empty / zero tensors** so the emitted stacks are always length `stackSize`.
- Pads for missing action/parameters are explicit, not omitted channels.

**Parameter packing (locked)**

Parameters are dynamic. Encoding uses a **fully learned encoder** that maps the structured parameter object → fixed-size vector for `param_stack`.

- The encoder itself is **deterministic** (same parameter input → same vector). This keeps stacks stable and training reproducible.
- Preventing “exact previous parameters → exact next parameters” is **not** done by making the encoder noisy. It is a property of the full decision context (intent, image stack, action stack, param stack) and of optional stochasticity on the **policy outputs** at inference time.

**Output of L1**

Layout 3 tensor stacks, always of length `stackSize` (padded while warming up).

---

## Tensor layout (L1 → L2) — locked

**Layout 3** is the contract:

```text
tuple(
  intent_stack,   # stacked tensor from array of intents
  image_stack,    # stacked tensor from array of prepared images
  action_stack,   # stacked tensor from array of actions
  param_stack,    # stacked tensor from array of parameters
)
```

L1 may keep modality arrays internally; conversion to these stacked tensors occurs only at the hand-off to L2.

---

## Intent handling (blanket + mid-stack change)

**Locked preference:** Intent is conceptually a **blanket** over the decision being made *now*.

**Practical rule for the buffer**

- L1 still records the intent that was active at each step into the per-slot history (so `intent_stack` is a real stack).
- At prediction time, the **current** intent is the primary conditioning signal (blanket).
- If intent changes in the middle of the stack:
  - Older slots keep the intent that was active when they were written.
  - The model can therefore *see* that a change occurred (via `intent_stack`).
  - The decision itself is still framed as “under the **current** intent.”

This avoids two failure modes:

1. True single-value blanket with no history → intent changes are invisible; the model cannot learn “we just switched task.”
2. Treating every past intent as equally important as the current one → dilutes the notion of “what am I doing right now.”

So: **stack of intents exists; current intent is special.**

---

## Layer 2 — Policy Core

**Input**

- The four Layout-3 stacks produced by L1 (each length `stackSize`).

**Responsibilities (high level)**

- Consume the historical context (visuals + intents + past actions + past parameters).
- Produce a **hybrid** decision:
  - **Discrete** head(s): next action (and optionally argument kind) via classification / cosine-over-vocabulary style.
  - **Continuous** head(s): spatial / geometric / other open parameters via regression.

**Statefulness switch (locked)**

| Switch | Behaviour |
|--------|-----------|
| **Off** (**default**) | Pure feed-forward across calls. All history that influences the decision lives in the L1 stacks. Inside one forward pass, any temporal operator over the stack is allowed (attention, LSTM unrolled over `stackSize`, mean-pool, etc.). |
| **On** | Stateful across calls. L2 may carry internal recurrent state (e.g. LSTM/GRU hidden state) that persists between forward passes, enabling context longer than `stackSize`. |

**Reset policy when switch is On (locked)**

| Phase | Rule |
|-------|------|
| **Inference** | Reset internal state on **major intent** change and on episode / task boundary. Definition of “major” intent is deferred. |
| **Per-step control** | Expose a `reset_state` flag on the forward path so the action executor can force a reset (or not) on any step. Default: `false`. |
| **Training** | **Match inference**: reset on episode boundary and on major intent change (per-env masks in batched training). Do **not** hard-reset every step — that would train away statefulness. |

When **Off**, there is no internal state to reset.  
When **On**, behaviour depends on carried state; the rules above keep train and inference aligned.

**What L2 does *not* own**

- Circular buffer / history bookkeeping (L1).  
- Raw image transforms (L1).  
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
- **options** — open-ended; may describe parameter type or related hints. **Included** in embedding computation when present.
- **description** — documentation only; excluded from computation.

### Parameters

- **Id** — type of the parameter (e.g. `Key`, `tap`, `box`).
- **options** — the value(s) (e.g. `[ESCAPE]`, `[0.254, 0.586]`).
- Encoded by the **fully learned parameter encoder** (deterministic). Description does not participate.

### Intent

Same base shape. Hierarchy (e.g. daily task → difficulty → dungeon) is expressed **inside** the intent item via `options` (and nested options if needed), **not** as an extra top-level argument alongside image / intent / action / parameters.

Prefer nested/hierarchical options or hierarchical Ids rather than a fifth channel.

Vocabularies remain **injectable** (not static). Placeholders are used until concrete sets are supplied.

### Id vs options embedding (locked)

For Action and Intent (and analogous discrete identities):

- **Separate vectors**: `emb_id = Embed(Id)`, `emb_opt = Encode(options)` (zero when empty).
- **Then fuse** (concat or gated sum) before temporal fusion / heads.

This keeps Id embeddings stable and deterministic while still letting options influence the representation.

---

## Data-flow sketch

```text
                    ┌─────────────────────────────────────┐
 current image ────►│                                     │
 current intent ───►│  L1  History / Context Buffer       │
 previous action ──►│   • transform image                 │
 previous params ──►│   • encode intent/action/params     │
                    │   • learned param encoder (det.)    │
                    │   • circular arrays (final-ready)   │
                    │   • pad to stackSize if needed      │
                    │   • emit Layout-3 tensor stacks     │
                    └──────────────────┬──────────────────┘
                                       │  (intent, image, action, param) stacks
                                       ▼
                    ┌─────────────────────────────────────┐
                    │  L2  Policy Core                    │
                    │   • stateful switch: off (default)  │
                    │                      | on           │
                    │   • reset: major intent / episode   │
                    │            + per-step flag          │
                    │   • temporal / context fusion       │
                    │   • discrete head(s)                │
                    │   • continuous head(s)              │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                         next action + continuous args
```

After execution, the caller (or a thin wrapper) feeds the *executed* action + parameters back as the next step’s `previous_action` / `previous_parameters`.

---

## Locked decisions summary

| Topic | Decision |
|-------|----------|
| L1 → L2 contract | **Tensor Layout 3** |
| L1 internal storage | Arrays per modality, already final-ready |
| Warm-up | Pad with empty / zero tensors → always length `stackSize` |
| `stackSize` | ∈ {2, 4, 8, 16, 32, 64, 128, 256} |
| Slot temporal alignment | **Action taken from this image** |
| L2 stateful switch | **Off by default**; On = carry internal recurrent state |
| L2 state reset (when On) | **Major intent** change + episode boundary; per-step `reset_state` flag for executor; **training matches inference** (not every-step reset) |
| Intent | Blanket for the *current* decision; per-slot history still stored in `intent_stack` |
| Vocabulary base | `{ Id, description, options }` — description never in computation |
| Action Id | Fixed; drives deterministic embedding |
| Parameters | Id = type, options = value(s); **fully learned encoder (deterministic)** |
| Id vs options embedding | **Separate vectors, then fuse** |
| Intent specialization | Nested/hierarchical **options** (or hierarchical Id), not a new top-level argument |
| Discrete vocabularies | Injectable / not static; placeholders until supplied |
| Non-copying of params | Enforced by full context + optional output stochasticity; **not** by noisy param encoding |

---

## Open decisions (deferred)

1. Definition of **major intent** (what counts as a major change for reset).  
2. Exact fusion operator for Id/options (concat vs gated sum) and embedding dimensions.  
3. Optional inference-time stochasticity on continuous / discrete heads (temperature, noise).

---

## Design principles

- Clear **separation of concerns**: L1 = history + tensorization; L2 = decision.  
- **Circular buffer** of fixed, power-of-two-friendly `stackSize`.  
- History contains **intent + prepared image + action taken from image + parameters**.  
- Hybrid output (discrete + continuous) lives in L2.  
- L2 statefulness is an explicit switch (default Off) with aligned train/inference reset rules.  
- Vocabularies are structured, injectable, and free of hard-coded closed sets.  
- Human-readable `description` never enters the computation graph.  
- Parameter encoding is learned and deterministic; decision non-determinism is optional and lives at the heads.
