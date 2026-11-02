# Implementation Details

**Source of truth:** `src/fluxCore/policy/vocabulary/`.

## 1. Architecture Overview

`VocabularyItem.toTensor` builds one vector. `Vocabulary._rebuildEmbedding` stacks those vectors.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/policy/vocabulary/__vocabulary.py` | `.docs/fluxCore/policy/vocabulary/vocabulary.md` | List, ids, embedding stack |
| `src/fluxCore/policy/vocabulary/__vocabularyItem.py` | `.docs/fluxCore/policy/vocabulary/vocabularyItem.md` | One row and `toTensor` |

## 3. Core Workflows & Data Flow

1. `add` appends a `VocabularyItem` (or builds one from a string id).
2. `_rebuildEmbedding` calls `toTensor` on each item and `torch.stack`s them.
3. `fuse=False` → width `dimension`. `fuse=True` → width `dimension * 2`.
4. `remove` filters by `id` and rebuilds.
