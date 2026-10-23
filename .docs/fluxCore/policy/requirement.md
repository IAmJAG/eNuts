# Requirements — DCPolicy

**Source of truth:** `DCPolicy` in `src/fluxCore/policy/__dcPolicy.py` (`CP_VERSION` 2.0).

## 1. Overview

- **Context:** intent blanket + carousel of `(visual, action, parameters)`
- **Out:** next discrete action + argument kind + argument payload
- **Options typing:** `ActionVocabulary`, `ArgumentKindVocabulary`, `IntentVocabulary`

## 2. Functional requirements

| ID | Requirement | Status |
|----|-------------|--------|
| FR-1 | Raw image in; policy owns transform | Done |
| FR-2 | Carousel length = `stackSize` ∈ {4, 8, 16, 32, 64} | Done |
| FR-3 | Accept interval = `durationSec / stackSize` when `timestamp` set | Done |
| FR-4 | Discrete typed vocabs: actions, argument kinds, intents | Done |
| FR-5 | Argument values open (spatial / key / text) | Done |
| FR-6 | Embeddings cached at init | Done |
| FR-7 | Weights separate from options (`VERSION` + `MODELSTATE`) | Done |
| FR-8 | Device construct/load (cuda-first, cpu fallback) | Done |
| FR-9 | Vocab checks on `PolicyOptions.validate()` | Done |
| FR-10 | `IntentVocabulary` / `IntentLabel` required on options | Done |
| FR-11 | Slot = (visual, action, parameters) | Done |
| FR-12 | Intent conditions pooled trajectory | Done |
| FR-13 | `forward`/`predict`(image, intent, action, parameters, timestamp?) | Done |

## 3. Closed vs open

| Closed | Open |
|--------|------|
| `ActionLabel` ids (incl. `NONE`) | x, y, box geometry |
| `ArgumentKindLabel` ids (incl. `none`) | key code, text string |
| `IntentLabel` ids | — |

## 4. Deferred

- Learned key/text value generation
- Training loop packaging
- Richer temporal encoder than mean pool
