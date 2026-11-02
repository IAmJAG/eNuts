# Requirements & Design Specifications

**Source of truth:** `src/fluxCore/policy/vocabulary/`.

## 1. Project Overview

Discrete vocabulary helpers. Not on the policy `forward` path.

## 2. Functional Requirements

- **FR-1:** An item has `id`, `description`, and `options`. Description is not embedded.
- **FR-2:** `toTensor` embeds `id` with `deterministicEmbedding`. With `fuse=True` it concatenates an options embedding of the same width.
- **FR-3:** `Vocabulary` stacks item tensors on dim 0. Empty vocab leaves `embeddings` as `None`.
- **FR-4:** `add` and `remove` rebuild the stack. Changing `fuse` rebuilds it.

## 3. Non-Functional Requirements

- **NFR-1:** Embeddings are deterministic for the same id or options dict.
- **NFR-2:** Default width is 128.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Not wired into the policy
- **Affected Modules:** `vocabulary/__vocabulary.py`, `vocabulary/__vocabularyItem.py`
- **Description of Standard / Best Practice:** Heads often look up the live vocab inside `forward`.
- **Divergence:** The policy emits raw head tensors. The caller owns decode.
- **Design Decision & Justification:** Code is the source of truth.
- **Code Doc Cross-Reference:** `vocabulary.md`, `vocabularyItem.md`.
