## Overview & Design Context

This directory documents the policy (model) component of eNuts.

The policy accepts a current intent key, visual input (ndarray/tensor), and a history of previous actions with their arguments, then produces the next discrete action key together with a variant argument payload.

* **Design Decision / Deviation Notes:** This is a redesign. The earlier architecture sketch lives at `.docs/hybrid_discrete_continuous_policy.md` and is retained only for historical reference. All current requirements are defined in `requirement.md` within this directory. Spatial arguments are normalized; the Policy Wrapper owns buffering, denormalization and execution.

---

## Classes

*(None yet — source implementation has not been created.)*

---

## Functions

*(None yet — source implementation has not been created.)*

---

## Constants & Globals

*(None yet — source implementation has not been created.)*

## Sample Usage

*(Pending implementation.)*
