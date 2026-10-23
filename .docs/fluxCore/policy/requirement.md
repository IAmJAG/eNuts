# Requirements — DCPolicy

**Source of truth:** `DCPolicy` in `src/fluxCore/policy/__dcPolicy.py`.

## 1. Overview

Discrete–continuous policy for UI/device automation.

**Context (target):**

- Per slot: **visual** + **action taken at that visual** + **parameters** of that action
- **Intent** is the blanket over the whole carousel / decision
- Model always receives the full joint context (explicit NONE/EMPTY pads when a slot has no action/params)

**Output:** next discrete action + argument kind + argument payload.

## 2. Functional requirements (current + target)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-1 | Raw image in; policy owns transform | Current |
| FR-2 | Carousel length = `stackSize` ∈ {4, 8, 16, 32, 64} | Current |
| FR-3 | Accept interval = `durationSec / stackSize` when `timestamp` provided | Current |
| FR-4 | Discrete vocabs: actions, argument kinds | Current |
| FR-5 | Argument values open (spatial / key / text) | Current |
| FR-6 | Embeddings cached at init | Current |
| FR-7 | Weights separate from options (`VERSION` + `MODELSTATE`) | Current |
| FR-8 | Device is construct/load arg (cuda-first, cpu fallback) | Current |
| FR-9 | Vocab null/empty checks live on `PolicyOptions.validate()` | Current |
| FR-10 | Discrete **intent** vocabulary | Target |
| FR-11 | Carousel slot = (visual, action, parameters) aligned in time | Target |
| FR-12 | Intent conditions the pooled trajectory (blanket) | Target |
| FR-13 | `forward`/`predict` accept image, intent, action, parameters, optional timestamp | Target |

## 3. Closed vs open

| Closed (vocabulary) | Open |
|---------------------|------|
| action labels | x, y, box geometry |
| argument kind labels | key code string, text string |
| intent labels | — |

## 4. Deferred (after target context)

- Learned key/text value generation
- Full training loop packaging
- Richer temporal encoder than mean pool (e.g. attention)
