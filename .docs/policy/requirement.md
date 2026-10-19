# Requirements & Design Specifications

## 1. Project Overview

This document captures the redesigned requirements for the policy (model) component of the eNuts automation system.

The policy is responsible for deciding the next discrete action and its continuous arguments given the current high-level intent, a temporal stack of sequential streaming images, and the history of previously executed actions together with their arguments.

This is a redesign relative to the earlier architecture note in `.docs/hybrid_discrete_continuous_policy.md`. The earlier document remains for historical reference; all new design and implementation work must follow the requirements stated here.

## 2. Functional Requirements

- **FR-1 (Policy Inputs):** The policy must accept exactly three inputs at inference time:
  1. Current intent.
  2. Stack of sequential streaming images (temporal visual context).
  3. Stack of previously taken actions together with their corresponding action arguments (action history).

- **FR-2 (Policy Outputs):** Given the inputs above, the policy must produce:
  1. The next action (discrete).
  2. The argument(s) that should accompany that action (continuous / structured parameters).

- **FR-3 (Stateless Inference Contract):** The policy itself is a pure function of the three supplied inputs. Any required history buffering, intent management, or frame accumulation is the responsibility of the surrounding runtime / service layer, not of the model weights.

## 3. Non-Functional Requirements

- **NFR-1:** The input and output interfaces must be stable and explicitly typed so that the policy can be trained offline and later loaded into the live eNuts process without interface drift.
- **NFR-2:** Documentation for every source file that implements or consumes the policy must follow the path-mirroring and triad rules defined in `.kilocode/rules/Documentation.md`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Scope of the current requirement document
- **Affected Modules:** Future `src/policy/` (or equivalent) package and its documentation under `.docs/policy/`.
- **Description of Standard / Best Practice:** A complete policy specification normally includes data schemas, action registry, continuous parameter definitions, network architecture, training regime, and runtime integration points.
- **Divergence:** This document intentionally contains only the core input/output contract supplied by the current redesign request.
- **Design Decision & Justification:** Incremental capture of requirements. Further details (schemas, architecture, training, integration) will be added in subsequent iterations once they are explicitly provided.
- **Code Doc Cross-Reference:** Will be reflected in the corresponding `implementation.md` and per-file documentation once source appears.

## 5. Open Items (to be resolved before implementation)

- Concrete type / schema of “intent”.
- Concrete representation of the image stack (shape, dtype, color space, temporal length, stride).
- Concrete schema of the action + argument history stack.
- Exact discrete action vocabulary / registry.
- Exact continuous / structured argument schema for each action.
- Training data format and labeling conventions.
- Runtime owner that assembles the three inputs and consumes the two outputs.
