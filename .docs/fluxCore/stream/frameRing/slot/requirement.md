# Requirements & Design Specifications

## 1. Project Overview
Slot cell and flags for the stream frame ring.

## 2. Functional Requirements
- **FR-1:** Four states only: EMPTY, FREE, WRITING, FILLED.
- **FR-2:** Payload read must not change state.
- **FR-3:** Writable means EMPTY or FREE.

## 3. Non-Functional Requirements
- **NFR-1:** No consumer-facing tag API on the slot.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: No INUSE flag
- **Affected Modules:** `slot/__slotFlag.py`, `slot/__ringSlot.py`
- **Divergence:** Earlier designs used INUSE on payload access.
- **Design Decision & Justification:** Sequential hold is expressed by remaining on `_order` until `release`, not by a payload getter side effect.
