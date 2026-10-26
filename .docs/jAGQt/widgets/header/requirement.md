# Requirements & Design Specifications

## 1. Project Overview
Header is the visual chrome for a Page title area.

## 2. Functional Requirements
- **FR-1:** Support optional icon with multiple placements relative to title/description.
- **FR-2:** All icon presentation details (position, size, colors) must be mutable after construction.
- **FR-3:** Constructor must not require icon layout arguments.

## 3. Non-Functional Requirements
- **NFR-1:** Changing any icon-related property must rebuild the internal layout safely.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Slim constructor
- **Affected Modules:** `jAGQt/widgets/header/__header.py`
- **Description of Standard / Best Practice:** Pass every option through `__init__`.
- **Divergence:** Only title / description / icon in `__init__`; remaining options are properties with defaults.
- **Design Decision & Justification:** Page builders and navigation tables pass title + description (+ icon path); layout tuning is rare and better as post-construction configuration.
- **Code Doc Cross-Reference:** header.md
