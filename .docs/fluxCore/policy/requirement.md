# Requirements & Design Specifications

## 1. Project Overview

Policy: image array → discrete action + argument kind + open argument value.

## 2. Functional Requirements

- **FR-1:** Input `[T,3,H,W]` or `[B,T,3,H,W]`.
- **FR-2:** One result per array.
- **FR-3:** Discrete **vocabularies** only for:
  - actions
  - argument kinds (`coordinate` | `box` | `key` | `text`)
- **FR-4:** Argument *values* are not vocabularies (spatial continuous; key/text open-ended).
- **FR-5:** Vocabularies are serializable (`Vocabulary` / `VocabularyItem`) and convert to embeddings via `toEmbedding` / `toEmbeddings`.
- **FR-6:** Vocabularies are fixed at construction / checkpoint load — not mutated at runtime.

## 3. Design Decisions

### Naming
Finite discrete sets are **vocabularies**, not “registry options.”

### Closed vs open
| Closed | Open |
|--------|------|
| action labels | x, y, box geometry |
| argument kind labels | key code string, text string |
