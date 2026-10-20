# Requirements & Design Specifications

## 1. Overview

Image array → `(actionKey, argument)`. Implementation: `src/fluxCore/policy/`.

## 2. Requirements

- **Vocabularies (finite):** actions, argument kinds.
- **Not vocabularies (open):** argument values — coordinates, boxes, key codes, free text.
- Vocabularies are serializable and produce embedding tensors.
- No runtime mutation of vocabularies.

## 3. Deferred

Intent, history, concrete key/text value generation, training packaging.
