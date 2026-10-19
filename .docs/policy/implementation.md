# Implementation Details

## 1. Architecture Overview

No source implementation exists yet. This file will be expanded once the concrete modules under `src/` are written.

The governing requirements (including locked schemas for intent, image stack, action registry, variant arguments, training data and the Policy Wrapper) are defined in `requirement.md`.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| *(pending)* | `.docs/policy/` | Policy model input/output contract and future implementation |

## 3. Core Workflows & Data Flow

At inference time the **Policy Wrapper** is expected to:

1. Maintain the image carousel (pre-process single frames, apply stride, keep last *N* frames).
2. Maintain the action-history buffer.
3. Hold the current intent key.
4. Call the pure policy with (intent key, visual tensor/stack, action history).
5. Receive (next action key, variant arguments).
6. Denormalize spatial arguments using the current device resolution and translate into a concrete `fluxCore` action.
7. Execute the action and optionally apply humanization (micro-jitter, delays).

The policy itself remains a pure function of its three inputs.

Further workflow detail will be added when the remaining open items in `requirement.md` are resolved and source appears.
