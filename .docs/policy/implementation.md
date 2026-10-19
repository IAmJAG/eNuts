# Implementation Details

## 1. Architecture Overview

Minimal policy: single image → discrete action key.

No source implementation exists yet. This file will be expanded when the first concrete module is written under `src/`.

Governing requirements are in `requirement.md`.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| *(pending)* | `.docs/policy/` | Minimal image-to-action policy |

## 3. Core Workflows & Data Flow

1. Receive one image.
2. Pre-process to the stable internal shape (currently targeted at 24×24×3).
3. Run the model.
4. Emit one of the four action keys: `down`, `up`, `move`, `inject`.

Further detail will be added with the first implementation.
