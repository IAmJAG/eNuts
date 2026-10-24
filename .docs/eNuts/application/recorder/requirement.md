# Requirements & Design Specifications

## 1. Project Overview
Controller for continuous key/gesture recording against a device stream for Policy datasets.

## 2. Functional Requirements
- **FR-1:** Implement `iKGRecorder`.
- **FR-2:** States: Idle, Recording only.
- **FR-3:** Collect key and pointer events with relative timestamps while Recording.
- **FR-4:** Save produces paired MP4 + event file (implementation deferred; naming by intent).
- **FR-5:** Event schema must later complement Policy action parameters.

## 3. Non-Functional Requirements
- **NFR-1:** No UI ownership; Page remains a view.
