# Implementation Details

## 1. Architecture Overview

No source implementation exists yet. This file will be expanded once the concrete modules under `src/policy/` (or the finally chosen package path) are written.

The governing requirements are defined in `requirement.md`.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| *(pending)* | `.docs/policy/` | Policy model input/output contract and future implementation |

## 3. Core Workflows & Data Flow

At inference time the surrounding runtime is expected to supply:

1. Current intent
2. Stack of sequential streaming images
3. Stack of previously taken actions + their arguments

The policy returns:

1. Next discrete action
2. Arguments for that action

Further workflow detail will be added when the runtime owner and data schemas are specified.
