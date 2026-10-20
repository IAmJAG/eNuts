# Requirements & Design Specifications

## 1. Overview

Image array → `(actionKey, variant argument)`. Implementation: `src/fluxCore/policy/`.

## 2. Requirements

- One process per image array.
- Action from registry fixed at policy construction.
- Arguments: `coordinate` | `box` | `key` | `text`.
- Key/text chosen from registries fixed at construction.
- **No runtime registry mutation.** Vocabulary changes are planned before a policy instance runs (train/load the right checkpoint).

## 3. Deferred

Intent, history, free-form text generation, training packaging.
