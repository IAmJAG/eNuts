### 1. Code Documentation Template (`filename.md`)

```markdown
## Overview & Design Context
Brief overview of what this file does.
* **Design Decision / Deviation Notes:** [If applicable, briefly explain any deviations from standard practices or specific architectural choices made for this file, referencing `requirement.md`].

---

## Classes

### `ClassName`
- **Purpose:** Brief description of the class and its responsibilities.
- **Methods:**
  - `methodName(argumentName)` -> Description of what the method does.

---

## Functions

### `functionName`
- **Arguments:** `argumentName` (Type) - Description of argument.
- **Returns:** `Type` - Description of return value.
- **Behavior:** Detailed description of the function's internal logic and side effects.

---

## Constants & Globals

### `C_CONSTANT_NAME`
- **Type:** `DataType`
- **Value / Description:** Purpose and definition of the constant.

### `G_GLOBAL_VAR`
- **Type:** `DataType`
- **Description:** Purpose of the global instance variable.

## Sample Usage

Here is an example of how to use the components within this file:

```python
# Initialization and basic usage
from module.path import ClassName, functionName, C_CONSTANT_NAME

lInstance = ClassName()
lResult = functionName(C_CONSTANT_NAME)
```
---

### 2. Requirements Document Template (`requirement.md`)

```markdown
# Requirements & Design Specifications

## 1. Project Overview
High-level description of the project goals, system scope, and operational context.

## 2. Functional Requirements
- **FR-1:** Description of functional requirement.
- **FR-2:** Description of functional requirement.

## 3. Non-Functional Requirements
- **NFR-1:** Performance, security, or maintainability target.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: `[Title of Non-Standard Practice or Architectural Trade-off]`
- **Affected Modules:** `eNuts/__shell.py`, ...
- **Description of Standard / Best Practice:** What is the usual/industry-standard way to solve this issue?
- **Divergence:** Detailed explanation of how and why the implementation diverges from standard practice.
- **Design Decision & Justification:** Rationale behind choosing this alternative approach (e.g., performance constraints, legacy compatibility, simplified execution model).
- **Code Doc Cross-Reference:** How this decision is reflected in individual file documentations.
```
### 3. Implementation Details Template (implementation.md)
```markdown
# Implementation Details

## 1. Architecture Overview
High-level overview of the implementation structure, module dependencies, and entry points.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/__shell.py` | `.docs/eNuts/shell.md` | Core shell execution wrapper |

## 3. Core Workflows & Data Flow
Detailed walkthrough of how components interact during execution.
```