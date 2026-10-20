# Requirements & Design Specifications

## 1. Project Overview

Policy: image array → action key + **variant** argument.

## 2. Functional Requirements

- **FR-1:** Input `[T,3,H,W]` or `[B,T,3,H,W]`.
- **FR-2:** One result per array.
- **FR-3:** MobileNetV3-Small backbone, optional freeze.
- **FR-4:** Action via cosine score on an action registry supplied at construction.
- **FR-5:** Arguments are variant: `coordinate` | `box` | `key` | `text`.
- **FR-6:** Key and text values are selected from registries supplied at construction (not free-form generation).
- **FR-7:** Registries are **not** mutated at runtime. Vocabulary growth is planned offline (new training / new checkpoint), not via a live `setRegistry`.

## 3. Design Decisions

### Vocabulary lifecycle
Weights and registries are fixed for a running policy instance. Changing the action/key/text set is a development/training decision: train or load a policy built for that set. Historical labels stay valid under the vocab they were annotated with.

### Variant arguments
A kind head chooses the argument type; spatial fields use a continuous head; key/text use the same embedding-scoring pattern as actions against their own registries.
