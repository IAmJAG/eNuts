# Requirements — DCPolicy

**Source of truth:** `DCPolicy` in `src/fluxCore/policy/__dcPolicy.py`.

## 1. Overview

Discrete–continuous policy for UI/device automation frames.

- **In:** one raw image (`ndarray` or `Tensor`)
- **Out:** discrete action key + argument kind + argument payload (spatial and/or open values)

## 2. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-1 | `forward` / `predict` accept a **raw** image; the policy owns transform and carousel |
| FR-2 | Image carousel length = `PolicyOptions.stackSize` ∈ {4, 8, 16, 32, 64} |
| FR-3 | Discrete vocabularies only for **actions** and **argument kinds** |
| FR-4 | Argument **values** are open (coordinate/box continuous; key/text free) |
| FR-5 | Vocab embeddings are computed at construction and **cached** (not live-resolved each step) |
| FR-6 | Vocabularies fixed for the policy instance / checkpoint pair — no runtime mutation |
| FR-7 | Weights persist separately from options (`VERSION` + `MODELSTATE`) |
| FR-8 | Device is a construct/load argument (default cuda, fallback cpu) |

## 3. Closed vs open

| Closed (vocabulary) | Open |
|---------------------|------|
| action labels | x, y, box geometry |
| argument kind labels | key code string, text string |

## 4. Deferred

- Intent channel
- Action history as model input
- Learned key/text value generation
- Full training loop packaging
