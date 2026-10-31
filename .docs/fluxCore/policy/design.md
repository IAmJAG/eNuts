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
L2 is **optionally stateful** via an explicit switch (see below).

---

## Layer 1 — History / Context Buffer

**Inputs on each step**

- `image` — current raw frame  
- `intent` — current intent (discrete label / id)  
- `previous_action` — action that was last executed (or pad)  
- `previous_parameters` — parameters that accompanied that action (or pad / empty)

**Responsibilities**

1. **Image preparation**  
   Own the visual transform pipeline (resize, normalize, etc.) so that what enters the buffer is already in the form the model expects.

2. **Parameter / discrete encoding**  
   Convert intent, action, and parameters into tensor-friendly representations (embeddings or packed feature vectors). Exact encoding schemes and vocabularies are deferred; placeholders are used for now.

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

- `image_t_prepared` is the transformed visual.
- `action_t` / `parameters_t` are the previous action/parameters relative to that image (or pads).  
  Exact temporal alignment remains an open contract decision.

**Buffer semantics**

- Capacity = `stackSize` ∈ {2, 4, 8, 16, 32, 64, 128, 256}.
- Strict circular: always length ≤ `stackSize`; once full, every push drops the oldest.
- **Warm-up:** pad missing slots with **empty / zero tensors** so the emitted stacks are always length `stackSize`.
- Pads for missing action/parameters are explicit, not omitted channels.

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

## Layer 2 — Policy Core

**Input**

- The four Layout-3 stacks produced by L1 (each length `stackSize`).

**Responsibilities (high level)**

- Consume the historical context (visuals + intents + past actions + past parameters).
- Produce a **hybrid** decision:
  - **Discrete** head(s): next action (and optionally argument kind) via classification / cosine-over-vocabulary style.
  - **Continuous** head(s): spatial / geometric / other open parameters via regression.

**Statefulness switch (locked)**

L2 exposes an explicit switch:

| Switch | Behaviour |
|--------|-----------|
| **Off** (default) | Pure feed-forward across calls. All history that influences the decision lives in the L1 stacks. Inside one forward pass, any temporal operator over the stack is allowed (attention, LSTM unrolled over `stackSize`, mean-pool, etc.). |
| **On** | Stateful across calls. L2 may carry internal recurrent state (e.g. LSTM/GRU hidden state) that persists between forward passes, enabling context longer than `stackSize`. |

When the switch is **Off**, the same stack always yields the same decision (given fixed weights).  
When the switch is **On**, behaviour also depends on the carried internal state; reset of that state at episode / task boundaries is required for deterministic restarts.

**What L2 does *not* own**

- Circular buffer / history bookkeeping (L1).  
- Raw image transforms (L1).  
- Long-term persistence of the L1 carousel across process restarts (unless later decided).

**Vocabularies**

Discrete vocabularies are **not static**. Placeholders are maintained; concrete sets will be supplied later. Design and interfaces must not assume fixed action / intent / argument-kind tables.

---

## Data-flow sketch

```text
                    ┌─────────────────────────────────────┐
 current image ────►│                                     │
 current intent ───►│  L1  History / Context Buffer       │
 previous action ──►│   • transform image                 │
 previous params ──►│   • encode intent/action/params     │
                    │   • circular arrays (final-ready)   │
                    │   • pad to stackSize if needed      │
                    │   • emit Layout-3 tensor stacks     │
                    └──────────────────┬──────────────────┘
                                       │  (intent, image, action, param) stacks
                                       ▼
                    ┌─────────────────────────────────────┐
                    │  L2  Policy Core                    │
                    │   • stateful switch: off | on       │
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
| L1 internal storage | Arrays per modality, already final-ready (e.g. transformed images) |
| Warm-up | Pad with empty / zero tensors → always length `stackSize` |
| `stackSize` | ∈ {2, 4, 8, 16, 32, 64, 128, 256} |
| Discrete vocabularies | Not static; placeholders only for now |
| L2 cross-call state | **Switch**: Off = pure feed-forward; On = stateful (internal recurrent state) |

---

## Open decisions (still to settle)

1. **Slot temporal alignment** — does `(image_t, action_t, params_t)` mean “action that led to this image” or “action taken from this image”?  
2. **Exact continuous parameter packing** and discrete placeholder shapes.  
3. **Default value of the L2 stateful switch** and reset policy when On.  
4. **Whether intent is stored per-slot, as a blanket value, or both.**

---

## Design principles

- Clear **separation of concerns**: L1 = history + tensorization; L2 = decision.  
- **Circular buffer** of fixed, power-of-two-friendly `stackSize`.  
- History contains **intent + prepared image + previous action + previous parameters**.  
- Hybrid output (discrete + continuous) lives in L2.  
- L2 statefulness is an explicit, controllable switch, not an implicit default.  
- Vocabularies remain injectable; no hard-coded closed sets in the core design.
